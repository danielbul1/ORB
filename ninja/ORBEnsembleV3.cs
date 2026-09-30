// ORB Ensemble v3 for NinjaTrader 8 (NinjaScript strategy), ported from pine/orb_ensemble.pine and
// orb/families.py ENSEMBLE_V3. Run on a 5-minute MNQ (or NQ) chart with ETH or RTH data; the logic uses
// New York regular hours (09:30-16:00 ET) itself.
//
// Per member (opening-range length 5/15/30/60 min), at the close of the bar that completes its range:
//   direction = sign(close - 09:30 open); trade only if it agrees with the overnight gap (09:30 open vs
//   prior RTH close), |body| >= 0.05 x RTH ATR14, price is on the trade side of RTH VWAP and of an RTH
//   EMA (200 one-minute bars = 40 five-minute bars), stop >= 4 x round-trip cost, and the trend-strength
//   gate tau = ln(close/open) / (sigma5 x sqrt(len/5)) >= 1.0 (sigma5 = std of RTH 5-min log returns,
//   averaged over the prior 20 days). Enter at the next bar open.
//   Stop 0.10 x ATR14, target 10R (native orders per entry signal), trail 0.3 x ATR14 behind the best
//   price once 2R in profit, flat at 15:55-bar close (and Lucid auto-flattens at 16:45 ET).
//
// Managed approach, EntryHandling.UniqueEntries + StopTargetHandling.PerEntryExecution: each member
// ("E5","E15","E30","E60") has its own stop-market and limit orders held at the broker, so a lost
// connection doesn't leave a position unprotected.
#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using NinjaTrader.Cbi;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class ORBEnsembleV3 : Strategy
    {
        private static readonly int[] Lens = { 5, 15, 30, 60 };
        private TimeZoneInfo ny;

        // daily state
        private double dH, dL, prevClose = double.NaN, lastRthClose = double.NaN, dayOpen, atr14 = double.NaN;
        private readonly List<double> trs = new List<double>();
        private double pv, vol, rthEma = double.NaN;
        private double sr, sr2; private int nr;
        private readonly List<double> sigs = new List<double>();
        private double sig5 = double.NaN;
        private readonly bool[] done = new bool[4];
        private readonly double[] best = new double[4];
        private readonly double[] entryPx = new double[4];
        private readonly int[] dirOf = new int[4];
        private readonly double[] riskOf = new double[4];
        private bool wasInRth;
        private double prevBarClose = double.NaN;

        [NinjaScriptProperty, Display(Name = "Stop x ATR14", Order = 1, GroupName = "Rules")] public double StopX { get; set; }
        [NinjaScriptProperty, Display(Name = "Target R (0 = none)", Order = 2, GroupName = "Rules")] public double TargetR { get; set; }
        [NinjaScriptProperty, Display(Name = "Min body x ATR14", Order = 3, GroupName = "Rules")] public double BodyMin { get; set; }
        [NinjaScriptProperty, Display(Name = "EMA length (RTH minutes)", Order = 4, GroupName = "Rules")] public int EmaMinutes { get; set; }
        [NinjaScriptProperty, Display(Name = "Round-trip cost (points)", Order = 5, GroupName = "Rules")] public double RtCost { get; set; }
        [NinjaScriptProperty, Display(Name = "Min stop x cost", Order = 6, GroupName = "Rules")] public double MinRiskX { get; set; }
        [NinjaScriptProperty, Display(Name = "Trail x ATR14", Order = 7, GroupName = "Rules")] public double TrailX { get; set; }
        [NinjaScriptProperty, Display(Name = "Trail arms at R", Order = 8, GroupName = "Rules")] public double TrailAt { get; set; }
        [NinjaScriptProperty, Display(Name = "Trend gate tau", Order = 9, GroupName = "Rules")] public double TauMin { get; set; }
        [NinjaScriptProperty, Display(Name = "Tau sigma days", Order = 10, GroupName = "Rules")] public int TauWin { get; set; }
        [NinjaScriptProperty, Display(Name = "Risk per member (USD), min 1 contract", Order = 11, GroupName = "Sizing")] public double RiskUsd { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "ORBEnsembleV3";
                Description = "ORB Ensemble v3 (5/15/30/60-min members), see github.com/danielbul1/ORB";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 4;
                EntryHandling = EntryHandling.UniqueEntries;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                IsExitOnSessionCloseStrategy = false;   // we flatten ourselves at 15:55 ET
                BarsRequiredToTrade = 1;
                StopX = 0.10; TargetR = 10; BodyMin = 0.05; EmaMinutes = 200; RtCost = 1.0; MinRiskX = 4;
                TrailX = 0.3; TrailAt = 2.0; TauMin = 1.0; TauWin = 20; RiskUsd = 100;
            }
            else if (State == State.Configure)
            {
                ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time");
            }
        }

        // Minutes after 09:30 ET at which the current bar CLOSES (NinjaTrader bar time = close time).
        private double BarEndMinute()
        {
            DateTime et = TimeZoneInfo.ConvertTime(Time[0], Core.Globals.GeneralOptions.TimeZoneInfo, ny);
            return (et.Hour * 60 + et.Minute) - (9 * 60 + 30);
        }

        protected override void OnBarUpdate()
        {
            if (CurrentBar < 1 || BarsPeriod.BarsPeriodType != BarsPeriodType.Minute) return;
            int barMin = BarsPeriod.Value;
            double barEnd = BarEndMinute();
            bool inRth = barEnd > 0 && barEnd <= 390;
            bool newDay = inRth && !wasInRth;

            if (newDay) StartDay();
            if (inRth)
            {
                if (!newDay && !double.IsNaN(prevBarClose))
                {
                    double lr = Math.Log(Close[0] / prevBarClose);
                    sr += lr; sr2 += lr * lr; nr++;
                }
                dH = Math.Max(dH, High[0]); dL = Math.Min(dL, Low[0]);
                double tp = (High[0] + Low[0] + Close[0]) / 3.0;
                pv += tp * Volume[0]; vol += Volume[0];
                double alpha = 2.0 / (EmaMinutes / (double)barMin + 1);
                rthEma = double.IsNaN(rthEma) ? Close[0] : alpha * Close[0] + (1 - alpha) * rthEma;
                lastRthClose = Close[0];
                prevBarClose = Close[0];
            }
            wasInRth = inRth;
            if (!inRth || double.IsNaN(atr14) || double.IsNaN(prevClose)) { ManageOpen(inRth, barEnd); return; }

            double vwap = vol > 0 ? pv / vol : Close[0];
            int gapDir = Math.Sign(dayOpen - prevClose);
            for (int i = 0; i < 4; i++)
            {
                int len = Lens[i];
                if (done[i] || Math.Abs(barEnd - len) > 1e-9) continue;
                done[i] = true;
                int d = Math.Sign(Close[0] - dayOpen);
                double riskPts = StopX * atr14;
                bool ok = d != 0 && d == gapDir
                    && Math.Abs(Close[0] - dayOpen) >= BodyMin * atr14
                    && d * (Close[0] - vwap) > 0
                    && (EmaMinutes == 0 || d * (Close[0] - rthEma) > 0)
                    && riskPts >= MinRiskX * RtCost
                    && (TauMin == 0 || (!double.IsNaN(sig5) && d * Math.Log(Close[0] / dayOpen) / (sig5 * Math.Sqrt(len / 5.0)) >= TauMin));
                if (!ok) continue;
                int qty = Math.Max(1, (int)Math.Floor(RiskUsd / (riskPts * Instrument.MasterInstrument.PointValue)));
                string id = "E" + len;
                dirOf[i] = d; riskOf[i] = riskPts; entryPx[i] = Close[0]; best[i] = double.NaN;
                // Bracket from the expected fill; refined from the real fill in OnExecutionUpdate.
                SetStopLoss(id, CalculationMode.Price, Close[0] - d * riskPts, false);
                if (TargetR > 0) SetProfitTarget(id, CalculationMode.Price, Close[0] + d * TargetR * riskPts);
                if (d > 0) EnterLong(qty, id); else EnterShort(qty, id);
            }
            ManageOpen(inRth, barEnd);
        }

        private void ManageOpen(bool inRth, double barEnd)
        {
            if (Position.MarketPosition == MarketPosition.Flat) return;
            if (inRth && barEnd >= 390)   // the 15:55-16:00 bar has closed: flat for the day
            {
                foreach (int len in Lens) { ExitLong("EOD", "E" + len); ExitShort("EOD", "E" + len); }
                return;
            }
            if (TrailX <= 0 || double.IsNaN(atr14)) return;
            for (int i = 0; i < 4; i++)
            {
                if (dirOf[i] == 0 || !done[i]) continue;
                int d = dirOf[i];
                double b = double.IsNaN(best[i]) ? (d > 0 ? High[0] : Low[0]) : (d > 0 ? Math.Max(best[i], High[0]) : Math.Min(best[i], Low[0]));
                best[i] = b;
                if (d * (b - entryPx[i]) >= TrailAt * riskOf[i])
                {
                    double stp = d > 0 ? Math.Max(entryPx[i] - riskOf[i], b - TrailX * atr14) : Math.Min(entryPx[i] + riskOf[i], b + TrailX * atr14);
                    SetStopLoss("E" + Lens[i], CalculationMode.Price, stp, false);
                }
            }
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity,
            MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (execution.Order == null || execution.Order.OrderState != OrderState.Filled) return;
            string name = execution.Order.Name;
            for (int i = 0; i < 4; i++)
            {
                if (name != "E" + Lens[i]) continue;
                int d = dirOf[i];
                entryPx[i] = price;   // refine the bracket from the real fill
                SetStopLoss(name, CalculationMode.Price, price - d * riskOf[i], false);
                if (TargetR > 0) SetProfitTarget(name, CalculationMode.Price, price + d * TargetR * riskOf[i]);
            }
        }

        private void StartDay()
        {
            if (!double.IsNaN(lastRthClose) && dH > 0)
            {
                double tr = double.IsNaN(prevClose) ? dH - dL : Math.Max(dH - dL, Math.Max(Math.Abs(dH - prevClose), Math.Abs(dL - prevClose)));
                trs.Add(tr); if (trs.Count > 14) trs.RemoveAt(0);
                atr14 = trs.Count == 14 ? trs.Average() : double.NaN;
                if (nr > 1)
                {
                    double m = sr / nr;
                    sigs.Add(Math.Sqrt(Math.Max(sr2 / nr - m * m, 0)));
                    if (sigs.Count > TauWin) sigs.RemoveAt(0);
                    sig5 = sigs.Count == TauWin ? sigs.Average() : double.NaN;
                }
            }
            prevClose = lastRthClose;
            dayOpen = Open[0];
            dH = High[0]; dL = Low[0];
            pv = 0; vol = 0; sr = 0; sr2 = 0; nr = 0;
            prevBarClose = double.NaN;
            for (int i = 0; i < 4; i++) { done[i] = false; dirOf[i] = 0; best[i] = double.NaN; }
        }
    }
}
