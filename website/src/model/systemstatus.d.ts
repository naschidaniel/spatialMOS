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
