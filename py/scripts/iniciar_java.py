import argparse
import os
from pathlib import Path
import socket
import subprocess

from dotenv import dotenv_values


def ambiente_java(python_dir):
    valores = dotenv_values(python_dir / ".env")
    token = valores.get("HEALTH_REPORT_SERVICE_TOKEN") or ""
    if len(token) < 32:
        raise ValueError("Configure HEALTH_REPORT_SERVICE_TOKEN com pelo menos 32 caracteres no py/.env.")
    env = os.environ.copy()
    env["HEALTH_REPORT_SERVICE_TOKEN"] = token
    env["HEALTH_REPORT_API_URL"] = "http://127.0.0.1:8000"
    env.pop("GEMINI_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verificar", action="store_true", help="Valida a configuracao sem iniciar o Java.")
    args = parser.parse_args()
    python_dir = Path(__file__).resolve().parents[1]
    java_dir = python_dir.parent.parent / "JAVA-ADVANCED" / "pettrack"
    try:
        env = ambiente_java(python_dir)
    except ValueError as ex:
        print(str(ex))
        return 2
    wrapper = java_dir / ("mvnw.cmd" if os.name == "nt" else "mvnw")
    if not wrapper.is_file():
        print("Projeto Java ou Maven Wrapper nao encontrado na estrutura esperada.")
        return 2
    if args.verificar:
        print("Configuracao valida.")
        return 0
    try:
        with socket.create_connection(("127.0.0.1", 8080), timeout=1):
            print("A porta 8080 esta ocupada. Encerre o Java atual com Ctrl+C e execute este comando novamente.")
            return 2
    except OSError:
        pass
    print("Iniciando aplicacao Java...")
    try:
        return subprocess.call([str(wrapper), "spring-boot:run"], cwd=java_dir, env=env)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
