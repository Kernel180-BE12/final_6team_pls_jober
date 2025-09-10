#!/usr/bin/env python3
"""
Final Project - All Services Startup Script
백엔드, 프론트엔드, AI 서비스를 한번에 실행하는 Python 스크립트
"""

import os
import sys
import subprocess
import platform
import time
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {
            'backend': {
                'name': 'Backend (Spring Boot)',
                'path': self.project_root / 'back',
                'command': self._get_backend_command(),
                'port': 8080,
                'url': 'http://localhost:8080'
            },
            'frontend': {
                'name': 'Frontend (Vue.js)',
                'path': self.project_root / 'front',
                'command': self._get_frontend_command(),
                'port': 5173,
                'url': 'http://localhost:5173'
            },
            'ai': {
                'name': 'AI Service (FastAPI)',
                'path': self.project_root / 'ai',
                'command': self._get_ai_command(),
                'port': 8000,
                'url': 'http://localhost:8000'
            }
        }
        self.processes = {}

    def _get_backend_command(self):
        """백엔드 실행 명령어 반환"""
        if platform.system() == "Windows":
            return ["gradlew.bat", "bootRun"]
        else:
            return ["./gradlew", "bootRun"]

    def _get_frontend_command(self):
        """프론트엔드 실행 명령어 반환"""
        return ["npm", "run", "dev"]

    def _get_ai_command(self):
        """AI 서비스 실행 명령어 반환"""
        return [sys.executable, "main.py"]

    def print_banner(self):
        """시작 배너 출력"""
        print("=" * 50)
        print("   Final Project - All Services Start")
        print("=" * 50)
        print()

    def check_dependencies(self):
        """의존성 확인"""
        print("🔍 Checking dependencies...")
        
        # Java 확인
        try:
            subprocess.run(["java", "-version"], capture_output=True, check=True)
            print("✅ Java is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Java is not installed or not in PATH")
            return False

        # Node.js 확인
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            print("✅ Node.js is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js is not installed or not in PATH")
            return False

        # Python 확인
        try:
            subprocess.run([sys.executable, "--version"], capture_output=True, check=True)
            print("✅ Python is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Python is not installed or not in PATH")
            return False

        print()
        return True

    def start_service(self, service_key, service_info):
        """개별 서비스 시작"""
        try:
            print(f"🚀 Starting {service_info['name']}...")
            
            # 서비스 디렉토리로 이동
            os.chdir(service_info['path'])
            
            # 프로세스 시작
            process = subprocess.Popen(
                service_info['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes[service_key] = process
            
            # 출력을 별도 스레드에서 처리
            def log_output():
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(f"[{service_info['name']}] {line.strip()}")
            
            thread = threading.Thread(target=log_output, daemon=True)
            thread.start()
            
            print(f"✅ {service_info['name']} started (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service_info['name']}: {e}")
            return False

    def start_all_services(self):
        """모든 서비스 시작"""
        print("🚀 Starting all services...")
        print()
        
        success_count = 0
        
        for service_key, service_info in self.services.items():
            if self.start_service(service_key, service_info):
                success_count += 1
            time.sleep(2)  # 서비스 간 시작 간격
        
        print()
        print("=" * 50)
        print("   Services Status")
        print("=" * 50)
        
        for service_key, service_info in self.services.items():
            status = "✅ Running" if service_key in self.processes else "❌ Failed"
            print(f"{service_info['name']:<25} {status}")
            print(f"  URL: {service_info['url']}")
        
        print()
        print("=" * 50)
        print("   All services are running!")
        print("=" * 50)
        print()
        print("Press Ctrl+C to stop all services...")
        
        return success_count == len(self.services)

    def stop_all_services(self):
        """모든 서비스 중지"""
        print("\n🛑 Stopping all services...")
        
        for service_key, process in self.processes.items():
            try:
                print(f"Stopping {self.services[service_key]['name']}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {self.services[service_key]['name']} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Force killing {self.services[service_key]['name']}...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {self.services[service_key]['name']}: {e}")
        
        print("✅ All services stopped")

    def run(self):
        """메인 실행 함수"""
        self.print_banner()
        
        # 의존성 확인
        if not self.check_dependencies():
            print("❌ Please install missing dependencies and try again.")
            return False
        
        # 모든 서비스 시작
        if not self.start_all_services():
            print("❌ Some services failed to start.")
            return False
        
        try:
            # 서비스들이 실행되는 동안 대기
            while True:
                time.sleep(1)
                
                # 프로세스 상태 확인
                for service_key, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️ {self.services[service_key]['name']} has stopped unexpectedly")
                        del self.processes[service_key]
                
        except KeyboardInterrupt:
            self.stop_all_services()
            return True

def main():
    """메인 함수"""
    manager = ServiceManager()
    success = manager.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
