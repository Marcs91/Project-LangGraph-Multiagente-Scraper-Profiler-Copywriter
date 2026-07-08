import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface RightPanelProps {
  apiToken: string;
  onApiTokenChange: (value: string) => void;
  headers: string;
  onHeadersChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export function RightPanel({
  apiToken,
  onApiTokenChange,
  headers,
  onHeadersChange,
  onSubmit,
  isLoading,
}: RightPanelProps) {
  return (
    <aside className="w-[260px] border-l border-border p-5 flex flex-col gap-6">
      <div>
        <h3 className="text-base font-bold text-foreground">API Token</h3>
        <p className="mt-1 text-xs text-muted-foreground">
          Ingresa tu API token para usar Scraper Web
        </p>
        <Input
          className="mt-2"
          placeholder="Ingresa tu API token"
          type="password"
          value={apiToken}
          onChange={(e) => onApiTokenChange(e.target.value)}
        />
        <p className="mt-1.5 text-xs text-muted-foreground">
          Encuentra tu API token en tu panel de control
        </p>
      </div>

      <div>
        <h3 className="text-base font-bold text-foreground">Headers</h3>
        <Input
          className="mt-2"
          placeholder="Ej: User-Agent, Accept, etc"
          value={headers}
          onChange={(e) => onHeadersChange(e.target.value)}
        />
        <p className="mt-1.5 text-xs text-muted-foreground">
          Personaliza los headers de la solicitud HTTP
        </p>
      </div>

      <p className="text-xs text-muted-foreground">
        Tu API token es confidencial. No lo compartas con nadie.
      </p>

      <Button
        onClick={onSubmit}
        disabled={isLoading}
        className="mt-auto w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-md shadow-emerald-500/20"
      >
        {isLoading ? "Procesando..." : "Enviar a Scraper Web"}
      </Button>
    </aside>
  );
}
