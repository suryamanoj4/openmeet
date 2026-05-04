import { get } from 'svelte/store';
import { authStore, isAuthenticated, currentUser } from '$lib/stores/auth';
import * as authService from '$lib/services/auth';

export interface AuthRequiredAction {
  kind: string;
  label: string;
  execute: () => void | Promise<void>;
  onCancel?: () => void;
}

let showOverlay = $state(false);
let overlayMode: 'login' | 'register' = $state('login');
let pendingAction: AuthRequiredAction | null = $state(null);
let overlayError = $state<string | null>(null);
let isSubmitting = $state(false);

function executePending() {
  const action = pendingAction;
  pendingAction = null;
  showOverlay = false;
  overlayMode = 'login';
  overlayError = null;
  isSubmitting = false;
  action?.execute();
}

function cancelPending() {
  const action = pendingAction;
  pendingAction = null;
  showOverlay = false;
  overlayMode = 'login';
  overlayError = null;
  isSubmitting = false;
  action?.onCancel?.();
}

export const ambientAuth = {
  get showOverlay() { return showOverlay; },
  set showOverlay(v: boolean) { showOverlay = v; },
  get overlayMode() { return overlayMode; },
  set overlayMode(v: 'login' | 'register') { overlayMode = v; },
  get pendingAction() { return pendingAction; },
  get overlayError() { return overlayError; },
  set overlayError(v: string | null) { overlayError = v; },
  get isSubmitting() { return isSubmitting; },
  set isSubmitting(v: boolean) { isSubmitting = v; },

  get user() { return get(currentUser); },
  get isAuthenticated() { return get(isAuthenticated); },

  requireAuth(action: AuthRequiredAction) {
    if (get(isAuthenticated)) {
      action.execute();
      return;
    }
    pendingAction = action;
    overlayMode = 'login';
    overlayError = null;
    showOverlay = true;
  },

  async login(email: string, password: string) {
    isSubmitting = true;
    overlayError = null;
    try {
      await authService.login(email, password);
      executePending();
    } catch (err) {
      overlayError = err instanceof Error ? err.message : 'Login failed';
      isSubmitting = false;
    }
  },

  async register(data: { email: string; password: string; first_name: string; last_name: string }) {
    isSubmitting = true;
    overlayError = null;
    try {
      await authService.register(data.email, data.password, data.first_name, data.last_name);
      executePending();
    } catch (err) {
      overlayError = err instanceof Error ? err.message : 'Registration failed';
      isSubmitting = false;
    }
  },

  async logout() {
    await authService.logout();
    cancelPending();
  },

  switchMode(mode: 'login' | 'register') {
    overlayMode = mode;
    overlayError = null;
  },

  cancel() {
    cancelPending();
  }
};
