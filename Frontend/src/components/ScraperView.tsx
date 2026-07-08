import { useState } from "react";
import { Info, Mail, Building2, Copy, Check, Globe, Loader2, Send } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { motion, AnimatePresence } from "framer-motion";

interface ScraperViewProps {
  url: string;
  onUrlChange: (value: string) => void;
  email: string;
  onEmailChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  result: {
    final_email: string;
    profile_data: string | null;
    target_url: string;
    run_id: string | null;
    email_sent_status: string | null;
  } | null;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 rounded-md bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 transition-colors hover:bg-indigo-100"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
      {copied ? "Copiado" : "Copiar"}
    </button>
  );
}

export function ScraperView({
  url,
  onUrlChange,
  email,
  onEmailChange,
  onSubmit,
  isLoading,
  result,
}: ScraperViewProps) {
  return (
    <main className="flex-1 p-8 overflow-y-auto">
      <div className="max-w-[780px]">
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <span className="h-7 w-1 rounded-full bg-amber-500" />
          Scraper Web
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Extrae datos de cualquier sitio web de forma rapida y sencilla
        </p>

        <div className="mt-8">
          <label className="text-sm font-medium text-foreground">
            URL del Sitio Web
          </label>
          <Input
            className="mt-2"
            placeholder="Ej: https://ejemplo.com"
            value={url}
            onChange={(e) => onUrlChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && url.trim() && email.trim() && !isLoading) onSubmit();
            }}
          />
        </div>

        <div className="mt-4">
          <label className="text-sm font-medium text-foreground flex items-center gap-1.5">
            <Mail size={14} className="text-indigo-500" />
            Email del Destinatario
          </label>
          <Input
            className="mt-2"
            type="email"
            placeholder="Ej: contacto@empresa.com"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && url.trim() && email.trim() && !isLoading) onSubmit();
            }}
          />
          <p className="mt-1 text-xs text-muted-foreground">
            El cold email generado se enviara automaticamente a esta direccion
          </p>
        </div>

        <Alert className="mt-6 border-amber-300/40 bg-amber-50 text-amber-900">
          <Info className="h-4 w-4 text-amber-600" />
          <AlertTitle className="text-amber-800 font-semibold">
            Nota sobre el scraping:
          </AlertTitle>
          <AlertDescription className="text-amber-700 text-sm">
            Asegurate de tener permiso para acceder al sitio web. El scraping
            debe cumplir con los terminos de servicio del sitio.
          </AlertDescription>
        </Alert>

        <Button
          onClick={onSubmit}
          disabled={isLoading || !url.trim() || !email.trim()}
          className="mt-6 w-full bg-indigo-500 hover:bg-indigo-400 text-white font-semibold py-5 text-base shadow-md shadow-indigo-500/20 disabled:opacity-50"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <Loader2 size={18} className="animate-spin" />
              Procesando pipeline...
            </span>
          ) : (
            "Iniciar Web Scraping"
          )}
        </Button>

        {/* Loading state */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-8"
            >
              <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-6">
                <div className="flex items-center gap-3">
                  <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100">
                    <Loader2 size={20} className="animate-spin text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-indigo-900">
                      Ejecutando pipeline de agentes...
                    </p>
                    <p className="text-xs text-indigo-600 mt-0.5">
                      Scraping &rarr; Analisis de negocio &rarr; Generacion de email
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  {["Scraper", "Profiler", "Copywriter"].map((agent, i) => (
                    <div
                      key={agent}
                      className="flex-1 rounded-lg bg-white/70 border border-indigo-100 px-3 py-2 text-center"
                    >
                      <p className="text-[10px] font-medium text-indigo-400 uppercase tracking-wide">
                        Agente {i + 1}
                      </p>
                      <p className="text-xs font-semibold text-indigo-800 mt-0.5">
                        {agent}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {result && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="mt-8 space-y-5"
            >
              {/* Header de resultados */}
              <div className="flex items-center gap-2 border-b border-border pb-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100">
                  <Check size={16} className="text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">
                    Pipeline completado
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Globe size={11} />
                    {result.target_url}
                    {result.run_id && (
                      <span className="ml-2 text-muted-foreground/60">
                        ID: {result.run_id}
                      </span>
                    )}
                  </p>
                </div>
              </div>

              {/* Estado de envío de email */}
              {result.email_sent_status && (
                <div className={`flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium ${
                  result.email_sent_status.startsWith("Email enviado")
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : "bg-red-50 text-red-700 border border-red-200"
                }`}>
                  <Send size={14} />
                  {result.email_sent_status}
                </div>
              )}

              {/* Cold Email */}
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="rounded-xl border border-indigo-200 bg-white shadow-sm overflow-hidden"
              >
                <div className="flex items-center justify-between border-b border-indigo-100 bg-indigo-50/50 px-5 py-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-100">
                      <Mail size={14} className="text-indigo-600" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-indigo-900">
                        Cold Email Generado
                      </p>
                      <p className="text-[11px] text-indigo-500">
                        Agente Copywriter
                      </p>
                    </div>
                  </div>
                  <CopyButton text={result.final_email} />
                </div>
                <div className="p-5">
                  <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed font-[inherit]">
                    {result.final_email}
                  </div>
                </div>
              </motion.div>

              {/* Perfil del Negocio */}
              {result.profile_data && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 }}
                  className="rounded-xl border border-amber-200 bg-white shadow-sm overflow-hidden"
                >
                  <div className="flex items-center justify-between border-b border-amber-100 bg-amber-50/50 px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-100">
                        <Building2 size={14} className="text-amber-600" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-amber-900">
                          Perfil del Negocio
                        </p>
                        <p className="text-[11px] text-amber-500">
                          Agente Profiler &mdash; Puntos de dolor, tecnologia,
                          oportunidades
                        </p>
                      </div>
                    </div>
                    <CopyButton text={result.profile_data} />
                  </div>
                  <div className="p-5">
                    <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed font-[inherit]">
                      {result.profile_data}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}
