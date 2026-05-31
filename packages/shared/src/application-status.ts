export const applicationStatuses = [
  "pending_cv",
  "cv_passed",
  "cv_failed",
  "test_submitted",
  "test_scored",
  "interviewing"
] as const;

export type ApplicationStatus = (typeof applicationStatuses)[number];

export const applicationStatusLabels: Record<ApplicationStatus, string> = {
  pending_cv: "CV review",
  cv_passed: "Test unlocked",
  cv_failed: "CV declined",
  test_submitted: "Test review",
  test_scored: "Scored",
  interviewing: "Interview"
};

export function canAccessTest(status: ApplicationStatus) {
  return ["cv_passed", "test_submitted", "test_scored", "interviewing"].includes(status);
}

export function canScheduleInterview(status: ApplicationStatus) {
  return status === "test_scored" || status === "interviewing";
}
