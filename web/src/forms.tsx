// Formularios de escritura (US-31.09..31.12): el error del servidor se muestra junto al campo que lo causó, sin perder
// lo escrito; al terminar bien se recargan los datos afectados.
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent, type ReactNode } from "react";
import { ApiError } from "./api";
import { describeError } from "./auth";

/** Mutación con recarga de claves y error estructurado (código, campo, mensaje). */
export function useAction<TArgs, TResult>(fn: (args: TArgs) => Promise<TResult>, invalidate: string[][] = []) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: () => invalidate.forEach((queryKey) => queryClient.invalidateQueries({ queryKey })),
  });
}

export function fieldOf(error: unknown): string | null {
  return error instanceof ApiError ? error.field : null;
}

/** Campo etiquetado; se marca como inválido si el error del servidor apunta a él. */
export function Field({
  label,
  name,
  error,
  children,
  hint,
  group = false,
}: {
  label: string;
  name: string;
  error: unknown;
  children: ReactNode;
  hint?: string;
  /** Grupo de controles con etiquetas propias (checkboxes, tablas): no se envuelve en <label> (HTML válido). */
  group?: boolean;
}) {
  const field = fieldOf(error);
  const invalid = field !== null && (field === name || field.startsWith(`${name}.`) || field.startsWith(`${name}[`));
  const body = (
    <>
      <span className="field-label" id={group ? `field-${name}` : undefined}>{label}</span>
      {children}
      {hint && <span className="small muted">{hint}</span>}
      {invalid && (
        <span className="field-error" role="alert">
          {describeError(error)}
        </span>
      )}
    </>
  );
  const className = `field${invalid ? " invalid" : ""}`;
  return group ? (
    <div className={className} data-field={name} role="group" aria-labelledby={`field-${name}`}>
      {body}
    </div>
  ) : (
    <label className={className} data-field={name}>
      {body}
    </label>
  );
}

/** Error general de un formulario (si no apunta a un campo concreto) o confirmación. */
export function FormStatus({ error, done, ok }: { error: unknown; done: boolean; ok: string }) {
  if (error && !fieldOf(error)) {
    return (
      <p className="error" role="alert">
        {describeError(error)}
      </p>
    );
  }
  if (error) return null;
  return done ? (
    <p className="flash" role="status">
      ✔ {ok}
    </p>
  ) : null;
}

/** Formulario desplegable («+ Nuevo …») para no ocupar la vista mientras no se usa. */
export function Disclosure({ label, children, open: initial = false }: { label: string; children: ReactNode; open?: boolean }) {
  const [open, setOpen] = useState(initial);
  return (
    <div className="disclosure">
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)}>
        {open ? "✕ Cerrar" : `+ ${label}`}
      </button>
      {open && <div className="disclosure-body">{children}</div>}
    </div>
  );
}

export function submit(handler: () => void) {
  return (e: FormEvent) => {
    e.preventDefault();
    handler();
  };
}

/** Líneas no vacías de un textarea (criterios de aceptación, uno por línea). */
export function lines(text: string): string[] {
  return text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
}
