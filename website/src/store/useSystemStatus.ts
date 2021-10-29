import { reactive, computed, unref } from "vue";
import { SystemCheck, SystemChecks, SystemStatus } from "../model";

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

  return {
    systemstatus,
    systemChecks,
    fetchSystemStatus,
  };
}
