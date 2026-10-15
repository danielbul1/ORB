// Compile-only stand-in for the part of the NinjaTrader 8 API that ninja/*.cs uses. Signatures follow the NT8
// help guide (ninjatrader.com/support/helpGuides/nt8). It has no behaviour: it catches C# syntax and type errors
// and misspelled members before NinjaTrader is available, but it is not the real API. NinjaTrader's own compile
// (NinjaScript Editor, F5) remains the final check; extend this file when a strategy uses a new member.
using System;

namespace NinjaTrader.Core
{
    public class GeneralOptions { public TimeZoneInfo TimeZoneInfo { get; set; } }
    public static class Globals { public static GeneralOptions GeneralOptions { get; set; } }
}

namespace NinjaTrader.Cbi
{
    public enum MarketPosition { Flat, Long, Short }
    public enum OrderState { Initialized, Submitted, Accepted, Working, PartFilled, Filled, Cancelled, Rejected, Unknown }
    public class Order { public string Name { get; set; } public OrderState OrderState { get; set; } }
    public class Execution { public Order Order { get; set; } }
    public class MasterInstrument { public double PointValue { get; set; } public double TickSize { get; set; } }
    public class Instrument { public MasterInstrument MasterInstrument { get; set; } }
    public class Position { public MarketPosition MarketPosition { get; set; } public int Quantity { get; set; } }
}

namespace NinjaTrader.Data
{
    public enum BarsPeriodType { Tick, Volume, Second, Minute, Day, Week, Month, Year }
    public class BarsPeriod { public BarsPeriodType BarsPeriodType { get; set; } public int Value { get; set; } }
}

namespace NinjaTrader.NinjaScript
{
    using NinjaTrader.Cbi;
    using NinjaTrader.Data;

    public enum State { SetDefaults, Configure, Active, DataLoaded, Historical, Transition, Realtime, Terminated, Finalized }
    public enum Calculate { OnBarClose, OnEachTick, OnPriceChange }
    public enum EntryHandling { AllEntries, UniqueEntries }
    public enum StopTargetHandling { PerEntryExecution, ByStrategyPosition }
    public enum CalculationMode { Currency, Percent, Price, Ticks }

    [AttributeUsage(AttributeTargets.Property)]
    public class NinjaScriptPropertyAttribute : Attribute { }

    public interface ISeries<T> { T this[int barsAgo] { get; } }

    public abstract class NinjaScriptBase
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public Calculate Calculate { get; set; }
        public State State { get; set; }
        public int CurrentBar { get; set; }
        public int BarsRequiredToTrade { get; set; }
        public BarsPeriod BarsPeriod { get; set; }
        public Instrument Instrument { get; set; }
        public ISeries<DateTime> Time { get; set; }
        public ISeries<double> Open { get; set; }
        public ISeries<double> High { get; set; }
        public ISeries<double> Low { get; set; }
        public ISeries<double> Close { get; set; }
        public ISeries<double> Volume { get; set; }
        protected virtual void OnStateChange() { }
        protected virtual void OnBarUpdate() { }
        public void Print(object value) { }
    }
}

namespace NinjaTrader.NinjaScript.Strategies
{
    using NinjaTrader.Cbi;

    public abstract class Strategy : NinjaScriptBase
    {
        public int EntriesPerDirection { get; set; }
        public EntryHandling EntryHandling { get; set; }
        public StopTargetHandling StopTargetHandling { get; set; }
        public bool IsExitOnSessionCloseStrategy { get; set; }
        public int ExitOnSessionCloseSeconds { get; set; }
        public Position Position { get; set; }
        public Order EnterLong(int quantity, string signalName) { return null; }
        public Order EnterShort(int quantity, string signalName) { return null; }
        public Order ExitLong(string signalName, string fromEntrySignal) { return null; }
        public Order ExitShort(string signalName, string fromEntrySignal) { return null; }
        public void SetStopLoss(string fromEntrySignal, CalculationMode mode, double value, bool isSimulatedStop) { }
        public void SetProfitTarget(string fromEntrySignal, CalculationMode mode, double value) { }
        public void CancelOrder(Order order) { }
        protected virtual void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity,
            MarketPosition marketPosition, string orderId, DateTime time) { }
    }
}
