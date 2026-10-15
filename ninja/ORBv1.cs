// ORB v1 for NinjaTrader 8 (NinjaScript strategy), ported from orb/families.py ORB_V1. Run on a 5-minute MNQ
// (or NQ) chart with ETH or RTH data; the logic uses New York regular hours (09:30-16:00 ET) itself.
//
// One trade per Session, decided when the 09:30-09:35 bar closes:
//   direction = sign(close - 09:30 open); trade only if it agrees with the overnight gap (09:30 open vs
//   prior RTH close), |body| >= 0.05 x RTH ATR14 and price is on the trade side of RTH VWAP. Enter at the
//   next bar open (09:35). Stop 0.10 x ATR14, target 10R, no trail.
//   Flat: market exit at the 15:55 bar open (placed when the 15:50-15:55 bar closes, so it fills the same day
//   on RTH or ETH charts), plus NinjaTrader's exit-on-session-close as a backstop for half days (13:00 ET
//   close). Lucid also auto-flattens at 16:45 ET. The engine exits at the 15:59 close, so exits can differ.
//
// The entry is named "E5" (the 5-minute Leg) so tools/nt_parity.py --rule v1 can match it against the engine.
// Stop and target are native orders held at the broker, so a lost connection doesn't leave the position open.
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
    public class ORBv1 : Strategy
    {
        private const int OrMinutes = 5;
        private const string Id = "E5";
        private TimeZoneInfo ny;

        // daily state
        private double dH, dL, prevClose = double.NaN, lastRthClose = double.NaN, dayOpen, atr14 = double.NaN;
        private readonly List<double> trs = new List<double>();
        private double pv, vol;
        private bool done, wasInRth;
        private int dir;
        private double riskPts;

        [NinjaScriptProperty, Display(Name = "Stop x ATR14", Order = 1, GroupName = "Rules")] public double StopX { get; set; }
        [NinjaScriptProperty, Display(Name = "Target R (0 = none)", Order = 2, GroupName = "Rules")] public double TargetR { get; set; }
        [NinjaScriptProperty, Display(Name = "Min body x ATR14", Order = 3, GroupName = "Rules")] public double BodyMin { get; set; }
        [NinjaScriptProperty, Display(Name = "Risk per trade (USD), min 1 contract", Order = 4, GroupName = "Sizing")] public double RiskUsd { get; set; }

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "ORBv1";
                Description = "ORB v1 (5-minute opening range, gap + VWAP filters, 10R), see github.com/danielbul1/ORB";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.UniqueEntries;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                IsExitOnSessionCloseStrategy = true;    // backstop for half days; normally we are flat at 15:55 ET
                ExitOnSessionCloseSeconds = 300;
                BarsRequiredToTrade = 1;
                StopX = 0.10; TargetR = 10; BodyMin = 0.05; RiskUsd = 80;
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
            double barEnd = BarEndMinute();
            bool inRth = barEnd > 0 && barEnd <= 390;
            bool newDay = inRth && !wasInRth;

            if (newDay) StartDay();
            if (inRth)
            {
                dH = Math.Max(dH, High[0]); dL = Math.Min(dL, Low[0]);
                double tp = (High[0] + Low[0] + Close[0]) / 3.0;
                pv += tp * Volume[0]; vol += Volume[0];
                lastRthClose = Close[0];
            }
            wasInRth = inRth;
            if (!inRth || double.IsNaN(atr14) || double.IsNaN(prevClose)) { ManageOpen(inRth, barEnd); return; }

            if (!done && Math.Abs(barEnd - OrMinutes) < 1e-9)
            {
                done = true;
                double vwap = vol > 0 ? pv / vol : Close[0];
                int d = Math.Sign(Close[0] - dayOpen);
                double risk = StopX * atr14;
                bool ok = d != 0 && d == Math.Sign(dayOpen - prevClose)
                    && Math.Abs(Close[0] - dayOpen) >= BodyMin * atr14
                    && d * (Close[0] - vwap) > 0;
                if (ok)
                {
                    int qty = Math.Max(1, (int)Math.Floor(RiskUsd / (risk * Instrument.MasterInstrument.PointValue)));
                    dir = d; riskPts = risk;
                    // Bracket from the expected fill; refined from the real fill in OnExecutionUpdate.
                    SetStopLoss(Id, CalculationMode.Price, Close[0] - d * risk, false);
                    if (TargetR > 0) SetProfitTarget(Id, CalculationMode.Price, Close[0] + d * TargetR * risk);
                    if (d > 0) EnterLong(qty, Id); else EnterShort(qty, Id);
                }
            }
            ManageOpen(inRth, barEnd);
        }

        private void ManageOpen(bool inRth, double barEnd)
        {
            if (Position.MarketPosition == MarketPosition.Flat) return;
            if (inRth && barEnd >= 385)   // the 15:50-15:55 bar has closed: exit at the next open, same day
            {
                ExitLong("EOD", Id); ExitShort("EOD", Id);
            }
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity,
            MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (execution.Order == null || execution.Order.OrderState != OrderState.Filled || execution.Order.Name != Id) return;
            // The engine measures the stop and target from the real 09:35 open, so refine the bracket from the fill.
            SetStopLoss(Id, CalculationMode.Price, price - dir * riskPts, false);
            if (TargetR > 0) SetProfitTarget(Id, CalculationMode.Price, price + dir * TargetR * riskPts);
        }

        private void StartDay()
        {
            if (!double.IsNaN(lastRthClose) && dH > 0)
            {
                double tr = double.IsNaN(prevClose) ? dH - dL : Math.Max(dH - dL, Math.Max(Math.Abs(dH - prevClose), Math.Abs(dL - prevClose)));
                trs.Add(tr); if (trs.Count > 14) trs.RemoveAt(0);
                atr14 = trs.Count == 14 ? trs.Average() : double.NaN;
            }
            prevClose = lastRthClose;
            dayOpen = Open[0];
            dH = High[0]; dL = Low[0];
            pv = 0; vol = 0;
            done = false; dir = 0;
        }
    }
}
