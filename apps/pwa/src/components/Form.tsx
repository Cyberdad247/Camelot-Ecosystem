// SPDX-License-Identifier: MIT

'use client';

import React, { createContext, useContext, useState, useCallback, useId } from 'react';

export type Rule<T = any> = {
  required?: boolean;
  message?: string;
  validator?: (value: T, allValues: Record<string, any>) => boolean | string | Promise<boolean | string>;
};

export interface FormInstance<T extends Record<string, any> = Record<string, any>> {
  getFieldValue: (name: keyof T | string) => any;
  getFieldsValue: () => T;
  setFieldValue: (name: keyof T | string, value: any) => void;
  setFieldsValue: (values: Partial<T>) => void;
  validateFields: () => Promise<{ values: T; valid: boolean; errors: Record<string, string> }>;
  resetFields: () => void;
  registerField: (name: string, rules?: Rule[]) => () => void;
  getFieldError: (name: string) => string | undefined;
}

const FormContext = createContext<FormInstance | null>(null);

export function useForm<T extends Record<string, any> = Record<string, any>>(
  initialValues?: Partial<T>
): [FormInstance<T>] {
  const [values, setValues] = useState<Record<string, any>>(initialValues || {});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [fieldRules, setFieldRules] = useState<Record<string, Rule[]>>({});

  const getFieldValue = useCallback((name: keyof T | string) => values[name as string], [values]);
  const getFieldsValue = useCallback(() => values as T, [values]);

  const setFieldValue = useCallback((name: keyof T | string, value: any) => {
    const key = name as string;
    setValues((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      if (prev[key]) {
        const next = { ...prev };
        delete next[key];
        return next;
      }
      return prev;
    });
  }, []);

  const setFieldsValue = useCallback((newValues: Partial<T>) => {
    setValues((prev) => ({ ...prev, ...newValues }));
  }, []);

  const resetFields = useCallback(() => {
    setValues(initialValues || {});
    setErrors({});
  }, [initialValues]);

  const registerField = useCallback((name: string, rules?: Rule[]) => {
    if (rules && rules.length > 0) {
      setFieldRules((prev) => ({ ...prev, [name]: rules }));
    }
    return () => {
      setFieldRules((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    };
  }, []);

  const getFieldError = useCallback((name: string) => errors[name], [errors]);

  const validateFields = useCallback(async () => {
    const newErrors: Record<string, string> = {};
    for (const [name, rules] of Object.entries(fieldRules)) {
      const val = values[name];
      for (const rule of rules) {
        if (rule.required && (val === undefined || val === null || val === '')) {
          newErrors[name] = rule.message || `${name} is required`;
          break;
        }
        if (rule.validator) {
          const res = await rule.validator(val, values);
          if (typeof res === 'string') {
            newErrors[name] = res;
            break;
          }
          if (res === false) {
            newErrors[name] = rule.message || `${name} validation failed`;
            break;
          }
        }
      }
    }
    setErrors(newErrors);
    return {
      values: values as T,
      valid: Object.keys(newErrors).length === 0,
      errors: newErrors,
    };
  }, [fieldRules, values]);

  const formInstance: FormInstance<T> = {
    getFieldValue,
    getFieldsValue,
    setFieldValue,
    setFieldsValue,
    validateFields,
    resetFields,
    registerField,
    getFieldError,
  };

  return [formInstance];
}

export interface FormProps<T extends Record<string, any> = Record<string, any>> {
  form?: FormInstance<T>;
  initialValues?: Partial<T>;
  onFinish?: (values: T) => void | Promise<void>;
  className?: string;
  children: React.ReactNode;
}

export function Form<T extends Record<string, any> = Record<string, any>>({
  form: propForm,
  initialValues,
  onFinish,
  className = '',
  children,
}: FormProps<T>) {
  const [internalForm] = useForm<T>(initialValues);
  const form = propForm || internalForm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { values, valid } = await form.validateFields();
    if (valid && onFinish) {
      await onFinish(values);
    }
  };

  return (
    <FormContext.Provider value={form as FormInstance}>
      <form onSubmit={handleSubmit} className={className} noValidate>
        {children}
      </form>
    </FormContext.Provider>
  );
}

export interface FormItemProps {
  name?: string;
  label?: React.ReactNode;
  rules?: Rule[];
  children: React.ReactElement | ((form: FormInstance) => React.ReactElement);
  className?: string;
  required?: boolean;
}

export function FormItem({
  name,
  label,
  rules,
  children,
  className = '',
  required,
}: FormItemProps) {
  const form = useContext(FormContext);
  const id = useId();

  React.useEffect(() => {
    if (!form || !name) return;
    const combinedRules = [...(rules || [])];
    if (required && !combinedRules.some((r) => r.required)) {
      combinedRules.unshift({ required: true, message: `${label || name} is required` });
    }
    return form.registerField(name, combinedRules);
  }, [form, name, rules, required, label]);

  const error = name && form ? form.getFieldError(name) : undefined;
  const isRequired = required || rules?.some((r) => r.required);

  let childNode: React.ReactNode = null;
  if (typeof children === 'function' && form) {
    childNode = children(form);
  } else if (React.isValidElement(children) && name && form) {
    const existingOnChange = (children.props as any).onChange;
    const value = form.getFieldValue(name) ?? '';
    childNode = React.cloneElement(children as React.ReactElement<any>, {
      id: (children.props as any).id || id,
      value,
      onChange: (e: any) => {
        const val = e && e.target ? (e.target.type === 'checkbox' ? e.target.checked : e.target.value) : e;
        form.setFieldValue(name, val);
        if (existingOnChange) existingOnChange(e);
      },
      className: `${(children.props as any).className || ''} ${
        error ? 'border-red-400 focus:border-red-400' : ''
      }`,
    });
  } else if (React.isValidElement(children)) {
    childNode = children;
  }

  return (
    <div className={`space-y-1 ${className}`}>
      {label && (
        <label
          htmlFor={id}
          className="block text-[11px] font-mono uppercase tracking-widest text-white/60"
        >
          {label}
          {isRequired && <span className="ml-1 text-gold-royal font-bold">*</span>}
        </label>
      )}
      <div>{childNode}</div>
      {error && (
        <p className="text-[10px] font-mono text-red-400 tracking-wider transition-all animate-pulse">
          {error}
        </p>
      )}
    </div>
  );
}

Form.Item = FormItem;
Form.useForm = useForm;
