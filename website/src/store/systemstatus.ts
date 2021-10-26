import { reactive, computed, unref } from "vue";
import { formatDateTime } from "../util/formatters";

export interface SystemCheck {
  taskName: string;
  taskFinishedTime: string;
  taskMaxAgeTime: string;
  maxAge: number;
  failed: boolean;
  complete?: boolean;
}

export interface SystemChecks {
  hourly: SystemCheck[];
  daily: SystemCheck[];
  weekly: SystemCheck[];
}

export interface SystemStatus {
  isLoading: boolean;
  isError: boolean;
  statusText: string;
  systemChecks: SystemChecks;
}

const systemstatus: SystemStatus = reactive({
  isLoading: false,
  isError: false,
  statusText: "",
  systemChecks: {
    hourly: [],
    daily: [],
    weekly: [],
  },
});

export function useSystemstatus() {
  async function fetchSystemStatus(
    url: string,
    options?: Record<string, unknown>
  ) {
    systemstatus.isLoading = true;
    systemstatus.systemChecks.hourly = [];
    systemstatus.systemChecks.daily = [];
    systemstatus.systemChecks.weekly = [];
    const res = await fetch(url, options);
    if (res.ok) {
      try {
        res.json().then((data) => {
          systemstatus.isError = false;
          systemstatus.statusText = res.statusText;
          data
            .sort((s1: SystemCheck, s2: SystemCheck) =>
              s1.taskName.localeCompare(s2.taskName)
            )
            .forEach((c: SystemCheck) => {
              c.failed = new Date().getTime() >= Date.parse(c.taskMaxAgeTime);
              if (c.maxAge < 90) {
                systemstatus.systemChecks.hourly.push(c);
              } else if (c.maxAge <= 1470) {
                systemstatus.systemChecks.daily.push(c);
              } else {
                systemstatus.systemChecks.weekly.push(c);
              }
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

  const systemChecks = computed((): SystemChecks => {
    return unref(systemstatus.systemChecks);
  });

  const updateTime = computed((): string => {
    const VITE_APP_VUE_APP_UPDATETIME = import.meta.env
      .VITE_APP_VUE_APP_UPDATETIME;
    return typeof VITE_APP_VUE_APP_UPDATETIME === "string"
      ? formatDateTime(parseInt(VITE_APP_VUE_APP_UPDATETIME.toString()))
      : formatDateTime(undefined);
  });

  const lastCommit = computed((): string => {
    return import.meta.env.VITE_APP_CURRENT_GIT_SHA;
  });

  return {
    lastCommit,
    systemstatus,
    systemChecks,
    updateTime,
    fetchSystemStatus,
  };
}
