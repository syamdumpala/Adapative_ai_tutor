"use client";

import { type FormEvent, useState } from "react";
import { AuthNotConnectedError } from "./api";
import type { FieldErrors } from "./types";

interface State<T> {
  values: T;
  errors: FieldErrors<T>;
  formError: string;
  formNotice: string;
  submitting: boolean;
}

export interface AuthFormOptions<T> {
  initial: T;
  validate: (values: T) => FieldErrors<T>;
  onSubmit: (values: T) => Promise<void>;
}

export interface TextFieldBinding {
  id: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled: boolean;
}

type StringKeys<T> = {
  [K in keyof T]: T[K] extends string ? K : never;
}[keyof T] &
  string;

export interface UseAuthForm<T> {
  values: T;
  errors: FieldErrors<T>;
  formError: string;
  formNotice: string;
  submitting: boolean;
  setField: <K extends keyof T>(name: K, value: T[K]) => void;
  setFieldError: <K extends keyof T>(name: K, message: string) => void;
  setNotice: (message: string) => void;
  setError: (message: string) => void;
  field: (name: StringKeys<T>) => TextFieldBinding;
  handleSubmit: (event: FormEvent) => void;
}

type Banner = { formError?: string; formNotice?: string };

function bannerFor(error: unknown): Banner {
  if (error instanceof AuthNotConnectedError) {
    return {
      formNotice:
        "The frontend is ready — accounts will work once the auth API is connected.",
    };
  }
  return {
    formError:
      error instanceof Error
        ? error.message
        : "Something went wrong. Please try again.",
  };
}

async function runSubmit<T>(
  options: AuthFormOptions<T>,
  values: T,
  apply: (patch: Partial<State<T>>) => void,
): Promise<void> {
  apply({ submitting: true, formError: "", formNotice: "" });
  try {
    await options.onSubmit(values);
  } catch (error) {
    apply(bannerFor(error));
  } finally {
    apply({ submitting: false });
  }
}

/** Controlled form state + validation + submit orchestration for the auth forms. */
export function useAuthForm<T>(options: AuthFormOptions<T>): UseAuthForm<T> {
  const [state, setState] = useState<State<T>>({
    values: options.initial,
    errors: {},
    formError: "",
    formNotice: "",
    submitting: false,
  });
  const apply = (patch: Partial<State<T>>) =>
    setState((prev) => ({ ...prev, ...patch }));
  const setFieldValue = <K extends keyof T>(name: K, value: T[K]) =>
    setState((s) => ({
      ...s,
      values: { ...s.values, [name]: value },
      errors: { ...s.errors, [name]: undefined },
      formError: "",
      formNotice: "",
    }));

  return {
    values: state.values,
    errors: state.errors,
    formError: state.formError,
    formNotice: state.formNotice,
    submitting: state.submitting,
    setField: setFieldValue,
    setFieldError: (name, message) =>
      setState((s) => ({ ...s, errors: { ...s.errors, [name]: message } })),
    setNotice: (message) => apply({ formNotice: message, formError: "" }),
    setError: (message) => apply({ formError: message, formNotice: "" }),
    field: (name) => ({
      id: String(name),
      value: state.values[name] as string,
      onChange: (value) => setFieldValue(name, value as T[typeof name]),
      error: state.errors[name],
      disabled: state.submitting,
    }),
    handleSubmit: (event) => {
      event.preventDefault();
      const errors = options.validate(state.values);
      if (Object.keys(errors).length > 0) {
        apply({ errors });
        return;
      }
      void runSubmit(options, state.values, apply);
    },
  };
}
