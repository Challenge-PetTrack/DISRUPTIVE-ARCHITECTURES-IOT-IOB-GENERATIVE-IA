"""Validacao paga opt-in: Java -> Python -> OpenAI, com fixture ficticia e sem Oracle.

Uso: python scripts/validar_health_report_real.py --maven C:/.../mvn.cmd
Requer JAVA_HOME apontando para JDK 21 e repositorio Java ao lado do repositorio IoT.
"""
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
    args = parser.parse_args()
    python_dir = Path(__file__).resolve().parents[1]
    iot = python_dir.parent
    java = iot.parent / "JAVA-ADVANCED" / "pettrack"
    env = os.environ.copy()
    env.update({k: v for k, v in dotenv_values(python_dir / ".env").items() if v is not None})
    if not env.get("OPENAI_API_KEY", "").strip() or len(env.get("HEALTH_REPORT_SERVICE_TOKEN", "")) < 32:
        print("Configuracao incompleta: chave OpenAI e token de servico sao necessarios.")
        return 2
    env["HEALTH_REPORT_MODE"] = "openai"
    env["PETTRACK_OPENAI_LIVE_TESTS"] = "true"
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
        # Java recebe somente o segredo de integracao; a chave OpenAI fica no processo Python.
        java_env.pop("OPENAI_API_KEY", None)
        output = iot / "docs" / "evidencias" / "health-report-openai-real.json"
        log = java / "target" / "health-report-openai-live.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run(
                [args.maven, "-o", "-Dtest=HealthReportOpenAIIT", f"-Dpettrack.health-report.evidence={output}", "test"],
                cwd=java, env=java_env, stdout=stream, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, timeout=120)
        print("Integracao real aprovada; evidencia ficticia salva." if result.returncode == 0
              else "Integracao real falhou; consulte o log de teste sem imprimir credenciais.")
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
