import type { ApplicationStatus } from "./application-status";

export type UserRole = "hr" | "candidate";

export type ScorecardCriterion = {
  id: string;
  label: string;
  weight: number;
  description: string;
};

export type AgentRunStatus = "queued" | "running" | "succeeded" | "failed";

export type ApplicationSummary = {
  id: string;
  candidateName: string;
  jobTitle: string;
  status: ApplicationStatus;
  cvScore?: number;
  totalScore?: number;
  updatedAt: string;
};
