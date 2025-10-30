"""
Benchmark Script for Guardian AI Agent Comparison
Compares langchain_agent.py vs guardian_agent_simple.py

Metrics:
- Execution time
- Number of violations found
- File discovery (files scanned)
- Consistency (multiple runs)
- Memory usage
- Pattern generation (LLM randomness analysis)
"""

import os
import sys
import json
import time
import psutil
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import gc
import re

# Add module paths
GUARDIAN_ROOT = Path(__file__).parent
sys.path.insert(0, str(GUARDIAN_ROOT))

class BenchmarkRunner:
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            'timestamp': self.timestamp,
            'test_runs': [],
            'summary': {}
        }
    
    def measure_memory(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def run_agent_test(self, agent_name: str, agent_script: str, query: str, run_number: int) -> Dict[str, Any]:
        """Run a single test with an agent and collect metrics using subprocess"""
        print(f"\n{'='*70}")
        print(f"Test Run #{run_number}: {agent_name}")
        print(f"{'='*70}")
        
        # Force garbage collection before test
        gc.collect()
        
        # Measure initial memory
        memory_start = self.measure_memory()
        
        # Start timer
        start_time = time.time()
        
        # Run the agent as a subprocess with REAL-TIME output
        try:
            cmd = [
                'python', 
                agent_script, 
                query
            ]
            
            print(f"\nRunning: python {Path(agent_script).name} <query>")
            print(f"Please wait... (this may take several minutes)\n")
            print("-" * 70)
            
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(GUARDIAN_ROOT),
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of crashing
            )
            
            # Collect output while showing it in real-time
            output_lines = []
            for line in process.stdout:
                print(line, end='')  # Print in real-time
                output_lines.append(line)
            
            # Wait for process to complete
            process.wait(timeout=600)
            
            execution_time = time.time() - start_time
            memory_end = self.measure_memory()
            memory_used = memory_end - memory_start
            
            print("-" * 70)
            
            # Parse output
            output_text = ''.join(output_lines)
            violations = []
            files_scanned = 0
            mode = "unknown"
            success = process.returncode == 0
            error = None
            
            if success:
                try:
                    # Look for JSON files created by the agent
                    json_files = list(Path(GUARDIAN_ROOT).glob("*.json"))
                    latest_json = max(json_files, key=lambda p: p.stat().st_mtime) if json_files else None
                    
                    if latest_json and (time.time() - latest_json.stat().st_mtime) < 60:
                        # File was created in the last 60 seconds
                        with open(latest_json, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                            violations = json_data.get('violations', [])
                            stats = json_data.get('stats', {})
                            mode = json_data.get('metadata', {}).get('mode', 'unknown')
                            
                            # Calculate files scanned
                            if 'pass1_files' in stats:
                                files_scanned = stats.get('pass1_files', 0) + stats.get('pass2_files', 0)
                            else:
                                files_scanned = stats.get('total_files', 0)
                    
                    # Fallback: try to extract from text output
                    if not violations:
                        violation_match = re.search(r'(\d+)\s+violations?', output_text, re.IGNORECASE)
                        files_match = re.search(r'(\d+)\s+files', output_text, re.IGNORECASE)
                        
                        if violation_match:
                            violations = [None] * int(violation_match.group(1))
                        if files_match:
                            files_scanned = int(files_match.group(1))
                    
                except Exception as e:
                    print(f"\nWarning: Could not parse results: {e}")
            else:
                error = "Process failed with non-zero exit code"
                print(f"\nError: {error}")
            
        except subprocess.TimeoutExpired:
            process.kill()
            execution_time = time.time() - start_time
            memory_end = self.measure_memory()
            memory_used = memory_end - memory_start
            
            violations = []
            files_scanned = 0
            mode = "timeout"
            success = False
            error = "Timeout after 600 seconds"
            
            print(f"\n\nError: Test timed out after 600 seconds")
        
        except Exception as e:
            execution_time = time.time() - start_time
            memory_end = self.measure_memory()
            memory_used = memory_end - memory_start
            
            violations = []
            files_scanned = 0
            mode = "error"
            success = False
            error = str(e)
            
            print(f"\n\nError during test: {e}")
        
        # Force garbage collection after test
        gc.collect()
        
        result_data = {
            'agent_name': agent_name,
            'run_number': run_number,
            'success': success,
            'execution_time_seconds': round(execution_time, 2),
            'memory_used_mb': round(memory_used, 2),
            'violations_count': len(violations),
            'files_scanned': files_scanned,
            'mode': mode,
            'error': error[:500] if error else None
        }
        
        print(f"\n{'='*70}")
        print(f"Results for {agent_name} Run #{run_number}:")
        print(f"  Success: {success}")
        print(f"  Time: {result_data['execution_time_seconds']}s")
        print(f"  Memory: {result_data['memory_used_mb']} MB")
        print(f"  Files: {files_scanned}")
        print(f"  Violations: {len(violations)}")
        print(f"  Mode: {mode}")
        print(f"{'='*70}")
        
        return result_data
    
    def run_benchmark(self, test_config: Dict[str, Any]):
        """Run a complete benchmark test"""
        query = test_config['query']
        num_runs = test_config.get('num_runs', 3)
        
        print(f"\n{'='*70}")
        print(f"🚀 BENCHMARK TEST: {test_config['name']}")
        print(f"{'='*70}")
        print(f"\nQuery: {query}")
        print(f"Number of runs per agent: {num_runs}")
        
        test_result = {
            'test_name': test_config['name'],
            'query': query,
            'num_runs': num_runs,
            'langchain_runs': [],
            'simple_runs': []
        }
        
        # Test LangChain Agent
        print(f"\n{'='*70}")
        print("🔷 Testing LangChain Agent")
        print(f"{'='*70}")
        
        langchain_script = str(GUARDIAN_ROOT / 'langchain_agent.py')
        
        for i in range(num_runs):
            try:
                run_result = self.run_agent_test("LangChain", langchain_script, query, i + 1)
                test_result['langchain_runs'].append(run_result)
                
                # Brief pause between runs
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ LangChain Agent Run {i+1} failed: {e}")
                test_result['langchain_runs'].append({
                    'agent_name': 'LangChain',
                    'run_number': i + 1,
                    'success': False,
                    'error': str(e)
                })
        
        # Test Simple Agent
        print(f"\n{'='*70}")
        print("🔶 Testing Simple Agent")
        print(f"{'='*70}")
        
        simple_script = str(GUARDIAN_ROOT / 'guardian_agent_simple.py')
        
        for i in range(num_runs):
            try:
                run_result = self.run_agent_test("Simple", simple_script, query, i + 1)
                test_result['simple_runs'].append(run_result)
                
                # Brief pause between runs
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Simple Agent Run {i+1} failed: {e}")
                test_result['simple_runs'].append({
                    'agent_name': 'Simple',
                    'run_number': i + 1,
                    'success': False,
                    'error': str(e)
                })
        
        # Analyze results
        self._analyze_test_results(test_result)
        
        self.results['test_runs'].append(test_result)
        
        return test_result
    
    def _analyze_test_results(self, test_result: Dict[str, Any]):
        """Analyze and compare test results"""
        print(f"\n{'='*70}")
        print("📈 ANALYSIS")
        print(f"{'='*70}")
        
        langchain_runs = test_result['langchain_runs']
        simple_runs = test_result['simple_runs']
        
        # Filter successful runs
        langchain_success = [r for r in langchain_runs if r.get('success')]
        simple_success = [r for r in simple_runs if r.get('success')]
        
        print(f"\n✅ Success Rate:")
        print(f"  LangChain: {len(langchain_success)}/{len(langchain_runs)} ({len(langchain_success)/len(langchain_runs)*100:.1f}%)")
        print(f"  Simple: {len(simple_success)}/{len(simple_runs)} ({len(simple_success)/len(simple_runs)*100:.1f}%)")
        
        if langchain_success and simple_success:
            # Average execution time
            lc_avg_time = sum(r['execution_time_seconds'] for r in langchain_success) / len(langchain_success)
            simple_avg_time = sum(r['execution_time_seconds'] for r in simple_success) / len(simple_success)
            
            print(f"\n⏱️  Average Execution Time:")
            print(f"  LangChain: {lc_avg_time:.2f}s")
            print(f"  Simple: {simple_avg_time:.2f}s")
            print(f"  Difference: {abs(lc_avg_time - simple_avg_time):.2f}s ({('LangChain faster' if lc_avg_time < simple_avg_time else 'Simple faster')})")
            
            # Average memory usage
            lc_avg_memory = sum(r['memory_used_mb'] for r in langchain_success) / len(langchain_success)
            simple_avg_memory = sum(r['memory_used_mb'] for r in simple_success) / len(simple_success)
            
            print(f"\n💾 Average Memory Usage:")
            print(f"  LangChain: {lc_avg_memory:.2f} MB")
            print(f"  Simple: {simple_avg_memory:.2f} MB")
            print(f"  Difference: {abs(lc_avg_memory - simple_avg_memory):.2f} MB")
            
            # Violations found
            lc_violations = [r['violations_count'] for r in langchain_success]
            simple_violations = [r['violations_count'] for r in simple_success]
            
            print(f"\n⚠️  Violations Found:")
            print(f"  LangChain: {lc_violations} (avg: {sum(lc_violations)/len(lc_violations):.1f})")
            print(f"  Simple: {simple_violations} (avg: {sum(simple_violations)/len(simple_violations):.1f})")
            
            # Consistency check
            lc_variance = max(lc_violations) - min(lc_violations) if lc_violations else 0
            simple_variance = max(simple_violations) - min(simple_violations) if simple_violations else 0
            
            print(f"\n🎯 Consistency (violation count variance):")
            print(f"  LangChain: {lc_variance} (range: {min(lc_violations) if lc_violations else 0}-{max(lc_violations) if lc_violations else 0})")
            print(f"  Simple: {simple_variance} (range: {min(simple_violations) if simple_violations else 0}-{max(simple_violations) if simple_violations else 0})")
            
            # Files scanned
            lc_files = [r['files_scanned'] for r in langchain_success]
            simple_files = [r['files_scanned'] for r in simple_success]
            
            print(f"\n📁 Files Scanned:")
            print(f"  LangChain: {lc_files} (avg: {sum(lc_files)/len(lc_files) if lc_files and isinstance(lc_files[0], (int, float)) else 'N/A'})")
            print(f"  Simple: {simple_files} (avg: {sum(simple_files)/len(simple_files) if simple_files and isinstance(simple_files[0], (int, float)) else 'N/A'})")
    
    def save_results(self):
        """Save benchmark results to JSON file"""
        output_file = self.output_dir / f"benchmark_{self.timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Also create a readable summary
        summary_file = self.output_dir / f"benchmark_{self.timestamp}_summary.txt"
        self._create_summary_report(summary_file)
        
        return output_file
    
    def _create_summary_report(self, output_file: Path):
        """Create a human-readable summary report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("GUARDIAN AI BENCHMARK SUMMARY\n")
            f.write("="*70 + "\n\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Total Tests: {len(self.results['test_runs'])}\n\n")
            
            for test in self.results['test_runs']:
                f.write(f"\n{'='*70}\n")
                f.write(f"Test: {test['test_name']}\n")
                f.write(f"{'='*70}\n\n")
                f.write(f"Query: {test['query']}\n\n")
                
                # LangChain results
                lc_runs = test['langchain_runs']
                lc_success = [r for r in lc_runs if r.get('success')]
                
                f.write("LangChain Agent:\n")
                f.write(f"  Success: {len(lc_success)}/{len(lc_runs)}\n")
                if lc_success:
                    avg_time = sum(r['execution_time_seconds'] for r in lc_success) / len(lc_success)
                    avg_violations = sum(r['violations_count'] for r in lc_success) / len(lc_success)
                    f.write(f"  Avg Time: {avg_time:.2f}s\n")
                    f.write(f"  Avg Violations: {avg_violations:.1f}\n")
                    f.write(f"  Violations Range: {[r['violations_count'] for r in lc_success]}\n")
                f.write("\n")
                
                # Simple results
                simple_runs = test['simple_runs']
                simple_success = [r for r in simple_runs if r.get('success')]
                
                f.write("Simple Agent:\n")
                f.write(f"  Success: {len(simple_success)}/{len(simple_runs)}\n")
                if simple_success:
                    avg_time = sum(r['execution_time_seconds'] for r in simple_success) / len(simple_success)
                    avg_violations = sum(r['violations_count'] for r in simple_success) / len(simple_success)
                    f.write(f"  Avg Time: {avg_time:.2f}s\n")
                    f.write(f"  Avg Violations: {avg_violations:.1f}\n")
                    f.write(f"  Violations Range: {[r['violations_count'] for r in simple_success]}\n")
                f.write("\n")
        
        print(f"📄 Summary saved to: {output_file}")


def main():
    """Run benchmark tests"""
    print("="*70)
    print("🏁 GUARDIAN AI BENCHMARK SUITE")
    print("="*70)
    print("\nThis will compare langchain_agent.py vs guardian_agent_simple.py")
    print("Testing performance, accuracy, and consistency.\n")
    
    # Initialize benchmark runner
    runner = BenchmarkRunner()
    
    # Define test configurations
    tests = [
        {
            'name': 'Hybrid Audit - 3DTinKer Repository',
            'query': 'Run an audit on https://github.com/Aadisheshudupa/3DTinKer to find all potential issues on basis of E:\\Hackathon\\GuardianAIV1\\GuardianAI\\Application_Development_Re-Engineering_Guidelines_0.pdf.',
            'num_runs': 3  # Run each agent 3 times for consistency testing
        }
    ]
    
    # Run all tests
    for test_config in tests:
        try:
            runner.run_benchmark(test_config)
        except Exception as e:
            print(f"\n❌ Benchmark test '{test_config['name']}' failed: {e}")
            traceback.print_exc()
    
    # Save results
    print(f"\n{'='*70}")
    print("💾 SAVING RESULTS")
    print(f"{'='*70}")
    
    output_file = runner.save_results()
    
    print(f"\n{'='*70}")
    print("✅ BENCHMARK COMPLETE")
    print(f"{'='*70}")
    print(f"\nResults saved to: {output_file}")
    print("\nCheck the benchmark_results/ directory for detailed reports.\n")


if __name__ == "__main__":
    main()
