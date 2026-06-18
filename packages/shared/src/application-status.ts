export const applicationStatuses = [
  "pending_cv",
  "cv_screened",
  "cv_passed",
  "cv_failed",
  "test_submitted",
  "test_scored",
  "test_failed",
  "interview_scheduled",
  "interview_completed",
  "interview_failed",
  "accepted"
] as const;

export type ApplicationStatus = (typeof applicationStatuses)[number];

export const applicationStatusLabels: Record<ApplicationStatus, string> = {
  pending_cv: "CV Pending",
  cv_screened: "Under Review",
  cv_passed: "CV Passed",
  cv_failed: "CV Failed",
  test_submitted: "Test Submitted",
  test_scored: "Test Scored",
  test_failed: "Test Failed",
  interview_scheduled: "Interview Scheduled",
  interview_completed: "Interview Completed",
  interview_failed: "Interview Failed",
  accepted: "Accepted"
};

export function canAccessTest(status: ApplicationStatus) {
  return [
    "cv_passed",
    "test_submitted",
    "test_scored",
    "test_failed",
    "interview_scheduled",
    "interview_completed",
    "interview_failed",
    "accepted"
  ].includes(status);
}

export function canScheduleInterview(status: ApplicationStatus) {
  return status === "test_scored" || status === "interview_scheduled";
}
