"""
scripts/notify.py
=================
Envia e-mail de notificação ao término do pipeline CI/CD.

Variáveis de ambiente esperadas (configuradas no GitHub Actions):
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS  – credenciais SMTP  (Secrets)
  NOTIFY_EMAIL                                 – destinatário      (Variable)
  TEST_RESULT, BUILD_RESULT, DEPLOY_RESULT     – resultados dos jobs
  RUN_URL                                      – link para o run
  COMMIT_SHA                                   – hash do commit
  BRANCH                                       – branch atual
"""

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_env(name: str, required: bool = True) -> str:
    value = os.environ.get(name, "")
    if required and not value:
        print(f"[notify] AVISO: variável de ambiente '{name}' não definida.", file=sys.stderr)
    return value


def status_emoji(result: str) -> str:
    return {"success": "✅", "failure": "❌", "skipped": "⏭️"}.get(result, "❓")


def build_html(test: str, build: str, deploy: str, run_url: str, sha: str, branch: str) -> str:
    overall = "✅ Pipeline concluído com SUCESSO" if all(
        r in ("success", "skipped") for r in (test, build, deploy)
    ) else "❌ Pipeline concluído com FALHA"

    return f"""
    <html><body style="font-family: sans-serif; color: #333; max-width: 600px; margin: auto;">
      <h2 style="border-bottom: 2px solid #0366d6; padding-bottom: 8px;">
        🗺️ pymap – Notificação de Pipeline
      </h2>
      <p style="font-size: 1.1em; font-weight: bold;">{overall}</p>
      <table style="width:100%; border-collapse: collapse; margin: 16px 0;">
        <tr style="background:#f6f8fa;">
          <th style="text-align:left; padding:8px; border:1px solid #e1e4e8;">Job</th>
          <th style="text-align:left; padding:8px; border:1px solid #e1e4e8;">Resultado</th>
        </tr>
        <tr>
          <td style="padding:8px; border:1px solid #e1e4e8;">🧪 Testes</td>
          <td style="padding:8px; border:1px solid #e1e4e8;">{status_emoji(test)} {test.upper()}</td>
        </tr>
        <tr>
          <td style="padding:8px; border:1px solid #e1e4e8;">📦 Build</td>
          <td style="padding:8px; border:1px solid #e1e4e8;">{status_emoji(build)} {build.upper()}</td>
        </tr>
        <tr>
          <td style="padding:8px; border:1px solid #e1e4e8;">🚀 Deploy</td>
          <td style="padding:8px; border:1px solid #e1e4e8;">{status_emoji(deploy)} {deploy.upper()}</td>
        </tr>
      </table>
      <p><strong>Branch:</strong> {branch}</p>
      <p><strong>Commit:</strong> <code>{sha[:8]}</code></p>
      <p>
        <a href="{run_url}" style="background:#0366d6; color:#fff; padding:8px 16px;
           text-decoration:none; border-radius:4px; display:inline-block;">
          Ver execução no GitHub Actions
        </a>
      </p>
      <hr style="margin-top:32px; border:none; border-top:1px solid #e1e4e8;">
      <p style="font-size:0.85em; color:#666;">
        Mensagem gerada automaticamente pelo pipeline CI/CD · pymap
      </p>
    </body></html>
    """


def main() -> None:
    smtp_host = get_env("SMTP_HOST")
    smtp_port = int(get_env("SMTP_PORT") or "587")
    smtp_user = get_env("SMTP_USER")
    smtp_pass = get_env("SMTP_PASS")
    to_email  = get_env("NOTIFY_EMAIL")

    test_result   = get_env("TEST_RESULT",   required=False) or "unknown"
    build_result  = get_env("BUILD_RESULT",  required=False) or "unknown"
    deploy_result = get_env("DEPLOY_RESULT", required=False) or "unknown"
    run_url       = get_env("RUN_URL",       required=False) or "#"
    commit_sha    = get_env("COMMIT_SHA",    required=False) or "N/A"
    branch        = get_env("BRANCH",        required=False) or "N/A"

    # Se variáveis SMTP não estiverem disponíveis, apenas loga e sai
    if not all([smtp_host, smtp_user, smtp_pass, to_email]):
        print("[notify] Variáveis SMTP incompletas — e-mail não enviado (modo dry-run).")
        print(f"[notify] test={test_result} | build={build_result} | deploy={deploy_result}")
        return

    subject = (
        f"[pymap CI] ✅ Pipeline OK — {branch}"
        if all(r in ("success", "skipped") for r in (test_result, build_result, deploy_result))
        else f"[pymap CI] ❌ Pipeline FALHOU — {branch}"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = to_email

    html_body = build_html(test_result, build_result, deploy_result, run_url, commit_sha, branch)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[notify] E-mail enviado com sucesso para {to_email}.")
    except Exception as exc:
        print(f"[notify] Falha ao enviar e-mail: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()