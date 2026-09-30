// Pantalla de acceso con token opaco acm_ (ADR-017); el token nunca sale de sessionStorage.
import { useState, type FormEvent } from "react";
import { describeError, useAuth } from "../auth";

export function Login() {
  const { login } = useAuth();
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(token);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  };
  return (
    <main className="login" id="main">
      <form onSubmit={submit} className="panel login-box" aria-labelledby="login-title">
        <h1 id="login-title">ACM — Agile Context Manager</h1>
        <p className="muted">
          Entra con tu token de ACM. Un administrador lo crea con <code>acm token create &lt;principal&gt;</code> o con la
          herramienta MCP <code>acm_token_create</code>.
        </p>
        <label htmlFor="token">Token</label>
        <input
          id="token"
          type="password"
          autoComplete="off"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="acm_…"
          required
        />
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        <button type="submit" className="primary" disabled={busy || !token.trim()}>
          {busy ? "Comprobando…" : "Entrar"}
        </button>
        <p className="muted small">El token se guarda solo en esta pestaña y se borra al cerrarla.</p>
      </form>
    </main>
  );
}
