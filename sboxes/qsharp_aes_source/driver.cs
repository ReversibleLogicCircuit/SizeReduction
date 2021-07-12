using System;
using System.Collections.Generic;
using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;
using Microsoft.Quantum.Simulation.Simulators.QCTraceSimulators;
using System.Diagnostics;

using Quantum.Benchmark;

namespace Quantum.MyProgram
{
	class Driver
	{
		static void Main(string[] args)
		{
			ResourcesEstimator estimator = new ResourcesEstimator();
			MainCircuit.Run(estimator).Wait();

			//Console.WriteLine(estimator.ToTSV());
			var data = estimator.Data;
			Console.WriteLine($"CNOTs\t\t: {data.Rows.Find("CNOT")["Sum"]}");
			Console.WriteLine($"QubitCliffords\t: {data.Rows.Find("QubitClifford")["Sum"]}");
			Console.WriteLine($"R\t\t: {data.Rows.Find("R")["Sum"]}");
			Console.WriteLine($"Measure\t\t: {data.Rows.Find("Measure")["Sum"]}");
			Console.WriteLine($"T\t\t: {data.Rows.Find("T")["Sum"]}");
			Console.WriteLine($"Depth\t\t: {data.Rows.Find("Depth")["Sum"]}");
			Console.WriteLine($"Width\t\t: {data.Rows.Find("Width")["Sum"]}");
			Console.WriteLine($"QubitCount\t: {data.Rows.Find("QubitCount")["Sum"]}");
			Console.WriteLine($"BorrowedWidth\t: {data.Rows.Find("BorrowedWidth")["Sum"]}");
			
			Console.WriteLine("\n");

			var sim = getTraceSimulator(false);
			var res = MainCircuit.Run(sim).Result;

			double tCountAll = sim.GetMetric<MainCircuit>(PrimitiveOperationsGroupsNames.T);
			double tCountCX = sim.GetMetric<MainCircuit>(PrimitiveOperationsGroupsNames.CNOT);
			double tCountClii = sim.GetMetric<MainCircuit>(PrimitiveOperationsGroupsNames.QubitClifford);
			double tCountM = sim.GetMetric<MainCircuit>(PrimitiveOperationsGroupsNames.Measure);
			double tCountR = sim.GetMetric<MainCircuit>(PrimitiveOperationsGroupsNames.R);
			double tDepthAll = sim.GetMetric<MainCircuit>(MetricsNames.DepthCounter.Depth);
			double allocatedQubits = sim.GetMetric<MainCircuit>(MetricsNames.WidthCounter.ExtraWidth);
			double returnWidth = sim.GetMetric<MainCircuit>(MetricsNames.WidthCounter.ReturnWidth);
			double inputWidth = sim.GetMetric<MainCircuit>(MetricsNames.WidthCounter.InputWidth);
			double borrowedWidth = sim.GetMetric<MainCircuit>(MetricsNames.WidthCounter.BorrowedWith);

			Console.WriteLine("#CX\t\t:" + tCountCX);
			Console.WriteLine("#Cli\t\t:" + tCountClii);
			Console.WriteLine("#R\t\t:" + tCountR);
			Console.WriteLine("#M\t\t:" + tCountM);
			Console.WriteLine("#T\t\t:" + tCountAll);
			Console.WriteLine("DepthAll\t:" + tDepthAll);
			Console.WriteLine("allocatedQubits\t:" + allocatedQubits);
			Console.WriteLine("inputWidth\t:" + inputWidth);
			Console.WriteLine("returnWidth\t:" + returnWidth);
			Console.WriteLine("borrowedWidth\t:" + borrowedWidth);
		}

		static QCTraceSimulator getTraceSimulator(bool full_depth)
		{
			var config = new QCTraceSimulatorConfiguration();
			config.UseDepthCounter = true;
			config.UseWidthCounter = true;
			config.UsePrimitiveOperationsCounter = true;
			config.ThrowOnUnconstrainedMeasurement = false;

			config.OptimizeDepth = true;

			if (full_depth)
			{
				config.TraceGateTimes[PrimitiveOperationsGroups.CNOT] = 1;
				config.TraceGateTimes[PrimitiveOperationsGroups.Measure] = 1;
				config.TraceGateTimes[PrimitiveOperationsGroups.QubitClifford] = 1;
			}

			return new QCTraceSimulator(config);
		}
	}
}
