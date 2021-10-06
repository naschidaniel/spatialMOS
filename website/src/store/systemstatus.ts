import { reactive, computed, unref } from "vue";
import { formatDateTime } from "../util/formatters";

export interface SystemCheck {
  taskName: string;
  taskFinishedTime: string;
  taskMaxAgeTime: string;
  failed: boolean;
}

export interface systemstatus {
  isLoading: boolean;
  isError: boolean;
  statusText: string;
  systemChecks: SystemCheck[];
}

const systemstatus: systemstatus = reactive({
  isLoading: false,
  isError: false,
  statusText: "",
  systemChecks: [],
});

export function useSystemstatus() {
  async function fetchSystemStatus(
    url: string,
    options?: Record<string, unknown>
  ) {
    systemstatus.isLoading = true;
    const res = await fetch(url, options);
    if (res.ok) {
      try {
        res.json().then((data) => {
          systemstatus.isError = false;
          systemstatus.statusText = res.statusText;
          systemstatus.systemChecks = data.map((c: SystemCheck) => {
            c.failed = new Date().getTime() >= Date.parse(c.taskMaxAgeTime);
            return c;
          });
        });
      } catch {
        systemstatus.isError = true;
        systemstatus.statusText = "Failed to convert Data";
      }
    } else {
      systemstatus.statusText = res.statusText;
      systemstatus.isError = true;
    }
    systemstatus.isLoading = false;
  }

  const systemChecks = computed((): SystemCheck[] => {
    const systemChecks = unref(systemstatus.systemChecks);
    return systemChecks.sort((s1, s2) =>
      s1.taskName > s2.taskName ? -1 : -1
    );
  });

  const updateTime = computed((): string => {
    const VITE_APP_VUE_APP_UPDATETIME =
      import.meta.env.VITE_APP_VUE_APP_UPDATETIME ?? undefined;
    return typeof VITE_APP_VUE_APP_UPDATETIME === "string"
      ? formatDateTime(parseInt(VITE_APP_VUE_APP_UPDATETIME.toString()))
      : formatDateTime(undefined);
  });

  const lastCommit = computed((): string => {
    return import.meta.env.VITE_APP_CURRENT_GIT_SHA as string;
  });

  return {
    lastCommit,
    systemstatus,
    systemChecks,
    updateTime,
    fetchSystemStatus,
  };
}
