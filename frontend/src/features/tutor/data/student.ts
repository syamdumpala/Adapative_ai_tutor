/** Default demo student first name. */
export const DEFAULT_STUDENT_NAME = "Maya";

/** Surname appended to the student's first name for display. */
export const STUDENT_LAST_NAME = "";

/** Two-letter initials from a name, mirroring the prototype's rule. */
export function initialsOf(name: string): string {
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "M";
  const second = parts[1]?.[0] ?? "";
  return (first + second).toUpperCase();
}

/** Full display name, e.g. "Maya Chen". */
export function fullName(firstName: string): string {
  return `${firstName} ${STUDENT_LAST_NAME}`;
}
