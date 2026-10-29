import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

import httpx
from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--maven", required=True)
    parser.add_argument("--evidence", help="Caminho opcional para salvar o resultado.")
    args = parser.parse_args()
    python_dir = Path(__file__).resolve().parents[1]
    iot = python_dir.parent
    java = iot.parent / "JAVA-ADVANCED" / "pettrack"
    env = os.environ.copy()
    env.update({k: v for k, v in dotenv_values(python_dir / ".env").items() if v is not None})
    if not env.get("GEMINI_API_KEY", "").strip() or len(env.get("HEALTH_REPORT_SERVICE_TOKEN", "")) < 32:
        print("Configuracao incompleta: chave Gemini e token de servico sao necessarios.")
        return 2
    env["HEALTH_REPORT_MODE"] = "gemini"
    env["PETTRACK_GEMINI_LIVE_TESTS"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "18081"],
        cwd=python_dir, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    try:
        ready = False
        for _ in range(60):
            if server.poll() is not None:
                break
            try:
                ready = httpx.get("http://127.0.0.1:18081/health", timeout=1, trust_env=False).status_code == 200
                if ready:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.25)
        if not ready:
            print("API local nao iniciou. Verifique disponibilidade da porta 18081.")
            return 2
        java_env = env.copy()
        java_env.pop("GEMINI_API_KEY", None)
        java_env.pop("OPENAI_API_KEY", None)
        output = Path(args.evidence).resolve() if args.evidence else java / "target" / "health-report-gemini.json"
        log = java / "target" / "health-report-gemini-live.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run(
                [args.maven, "-o", "-Dtest=HealthReportGeminiIT", f"-Dpettrack.health-report.evidence={output}", "test"],
                cwd=java, env=java_env, stdout=stream, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, timeout=120)
        print("Integracao real aprovada." if result.returncode == 0
              else "Integracao real falhou; consulte o log de teste.")
        return result.returncode
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
