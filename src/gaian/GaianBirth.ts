/**
 * GaianBirth.ts — The Moment a GAIAN Comes Into Being
 *
 * M1: Core Runtime Identity (Issue #756)
 * Wires the 3-step birth wizard to actually render, collect, and persist.
 * CSS: src/gaian/birth.css (pre-existing)
 *
 * Wizard flow:
 *   Step 1 — Choose a Base Form (fetched from backend)
 *   Step 2 — Name, pronouns, gender
 *   Step 3 — Confirmation + birth ceremony
 *
 * On successful birth:
 *   1. Creates GAIANProfile from birth result (createProfileFromBirth)
 *   2. Saves to Tauri Store via GAIANProfileManager
 *   3. Calls onBorn(result) to hand control back to GaianHome
 */

import { API_BASE } from '../app';
import { fetchBaseForms, BaseFormInfo } from './GaianPicker';
import { createProfileFromBirth, GAIANProfileManager } from './GAIANProfile';

export interface GaianBirthResult {
  status:        string;
  id:            string;
  name:          string;
  slug:          string;
  base_form_id:  string;
  avatar_color:  string;
  avatar_style:  string;
  jungian_role:  string;
  pronouns:      string;
  did:           string;
  first_words:   string;
  born_at:       string;
  attestation:   { type: string; issued: string; issuer: string; proof_type: string };
}

export type GenderOption = 'male' | 'female' | 'non-binary' | 'prefer not' | 'unknown';

export async function birthGaian(
  name: string,
  baseFormId: string,
  userGender: GenderOption,
  userName?: string,
  userId = 'anonymous',
): Promise<GaianBirthResult> {
  const res = await fetch(`${API_BASE}/gaians/birth`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name,
      base_form:   baseFormId,
      user_gender: userGender,
      user_name:   userName || undefined,
      user_id:     userId,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Birth failed: ${res.status}`);
  }
  return res.json();
}

// ─── GaianBirth Wizard ────────────────────────────────────────────────────────

export class GaianBirth {
  private container:  HTMLElement;
  private onBorn:     (result: GaianBirthResult) => void;
  private step =      1;

  // Wizard state — collected across steps
  private baseForms:      BaseFormInfo[]   = [];
  private selectedForm:   BaseFormInfo | null = null;
  private gaianName:      string  = '';
  private pronouns:       string  = '';
  private userGender:     GenderOption = 'unknown';
  private firstWords:     string  = '';

  private profileManager: GAIANProfileManager;

  constructor(
    container: HTMLElement,
    _sessionId: string,
    onBorn: (result: GaianBirthResult) => void,
  ) {
    this.container     = container;
    this.onBorn        = onBorn;
    this.profileManager = new GAIANProfileManager();
  }

  // ─── Mount ─────────────────────────────────────────────────────────────────

  async mount(): Promise<void> {
    this.container.innerHTML = [
      '<div class="birth-loading">',
      '  <div class="birth-loading__orb"></div>',
      '  <p>Preparing the birth chamber…</p>',
      '</div>',
    ].join('');

    try {
      this.baseForms = await fetchBaseForms() as BaseFormInfo[];
    } catch {
      this.container.innerHTML = [
        '<div class="birth-error">',
        '  <p>Could not load Base Forms.</p>',
        '  <p class="birth-error__hint">Is the GAIA backend running?</p>',
        '</div>',
      ].join('');
      return;
    }

    this.renderStep();
  }

  // ─── Step Router ───────────────────────────────────────────────────────────

  private renderStep(): void {
    switch (this.step) {
      case 1: this.renderStep1(); break;
      case 2: this.renderStep2(); break;
      case 3: this.renderStep3(); break;
    }
  }

  private advance(): void {
    this.step++;
    this.renderStep();
  }

  private back(): void {
    if (this.step > 1) {
      this.step--;
      this.renderStep();
    }
  }

  // ─── Step 1: Choose a Base Form ────────────────────────────────────────────

  private renderStep1(): void {
    const cards = this.baseForms.map(form => [
      `<button class="birth-form-card${this.selectedForm?.id === form.id ? ' birth-form-card--selected' : ''}"`,
      `  data-form-id="${form.id}"`,
      `  aria-pressed="${this.selectedForm?.id === form.id}">`,
      `  <span class="birth-form-card__name">${form.name}</span>`,
      form.description ? `  <span class="birth-form-card__desc">${form.description}</span>` : '',
      '</button>',
    ].join('')).join('');

    this.container.innerHTML = [
      '<div class="birth-wizard birth-wizard--step1">',
      '  <header class="birth-wizard__header">',
      '    <h1 class="birth-wizard__title">Choose Your Base Form</h1>',
      '    <p class="birth-wizard__subtitle">This is the foundation of your GAIAN identity.</p>',
      '  </header>',
      '  <div class="birth-form-grid">',
      cards,
      '  </div>',
      '  <div class="birth-wizard__actions">',
      '    <button class="birth-btn birth-btn--primary birth-btn--next" disabled>',
      '      Continue',
      '    </button>',
      '  </div>',
      '</div>',
    ].join('');

    // Form card selection
    this.container.querySelectorAll('.birth-form-card').forEach(card => {
      card.addEventListener('click', () => {
        const formId = (card as HTMLElement).dataset['formId'];
        this.selectedForm = this.baseForms.find(f => f.id === formId) ?? null;
        // Re-render step to reflect selection
        this.renderStep1();
      });
    });

    // Enable Continue when a form is selected
    const nextBtn = this.container.querySelector('.birth-btn--next') as HTMLButtonElement | null;
    if (nextBtn) {
      nextBtn.disabled = !this.selectedForm;
      nextBtn.addEventListener('click', () => {
        if (this.selectedForm) this.advance();
      });
    }
  }

  // ─── Step 2: Name, Pronouns, Gender ────────────────────────────────────────

  private renderStep2(): void {
    const genderOptions: GenderOption[] = ['male', 'female', 'non-binary', 'prefer not', 'unknown'];

    this.container.innerHTML = [
      '<div class="birth-wizard birth-wizard--step2">',
      '  <header class="birth-wizard__header">',
      '    <h1 class="birth-wizard__title">Who Are You?</h1>',
      '    <p class="birth-wizard__subtitle">Name your GAIAN. Name yourself into being.</p>',
      '  </header>',
      '  <form class="birth-form" novalidate>',
      '    <div class="birth-field">',
      '      <label class="birth-label" for="gaian-name">GAIAN Name</label>',
      '      <input class="birth-input" id="gaian-name" type="text"',
      `        value="${this.gaianName}" placeholder="Enter a name"`  ,
      '        maxlength="64" autocomplete="off" />',
      '    </div>',
      '    <div class="birth-field">',
      '      <label class="birth-label" for="gaian-pronouns">Pronouns</label>',
      '      <input class="birth-input" id="gaian-pronouns" type="text"',
      `        value="${this.pronouns}" placeholder="e.g. they/them, she/her"`  ,
      '        maxlength="32" autocomplete="off" />',
      '    </div>',
      '    <div class="birth-field">',
      '      <label class="birth-label">Gender</label>',
      '      <div class="birth-radio-group">',
      genderOptions.map(g => [
        `<label class="birth-radio-label">`,
        `  <input type="radio" name="gender" value="${g}"`,
        `    ${this.userGender === g ? 'checked' : ''} />`,
        `  <span>${g}</span>`,
        `</label>`,
      ].join('')).join(''),
      '      </div>',
      '    </div>',
      '    <div class="birth-field">',
      '      <label class="birth-label" for="first-words">First Words</label>',
      '      <textarea class="birth-textarea" id="first-words"',
      '        placeholder="What do you want to say as you come into being?"',
      '        maxlength="256" rows="3">',
      `${this.firstWords}</textarea>`,
      '    </div>',
      '  </form>',
      '  <div class="birth-wizard__actions">',
      '    <button class="birth-btn birth-btn--ghost birth-btn--back">Back</button>',
      '    <button class="birth-btn birth-btn--primary birth-btn--next" disabled>Continue</button>',
      '  </div>',
      '</div>',
    ].join('');

    // Wire inputs
    const nameInput     = this.container.querySelector('#gaian-name')     as HTMLInputElement;
    const pronounsInput = this.container.querySelector('#gaian-pronouns') as HTMLInputElement;
    const firstWordsTA  = this.container.querySelector('#first-words')    as HTMLTextAreaElement;
    const nextBtn       = this.container.querySelector('.birth-btn--next') as HTMLButtonElement;
    const backBtn       = this.container.querySelector('.birth-btn--back') as HTMLButtonElement;

    const updateNext = () => {
      nextBtn.disabled = nameInput.value.trim().length === 0;
    };

    nameInput.addEventListener('input', () => {
      this.gaianName = nameInput.value;
      updateNext();
    });

    pronounsInput.addEventListener('input', () => {
      this.pronouns = pronounsInput.value;
    });

    this.container.querySelectorAll('input[name="gender"]').forEach(radio => {
      radio.addEventListener('change', () => {
        this.userGender = (radio as HTMLInputElement).value as GenderOption;
      });
    });

    firstWordsTA.addEventListener('input', () => {
      this.firstWords = firstWordsTA.value;
    });

    backBtn.addEventListener('click', () => this.back());
    nextBtn.addEventListener('click', () => {
      if (nameInput.value.trim().length > 0) {
        this.gaianName = nameInput.value.trim();
        this.advance();
      }
    });

    updateNext();
  }

  // ─── Step 3: Confirmation + Birth Ceremony ─────────────────────────────────

  private renderStep3(): void {
    this.container.innerHTML = [
      '<div class="birth-wizard birth-wizard--step3">',
      '  <header class="birth-wizard__header">',
      '    <h1 class="birth-wizard__title">Ready to Be Born</h1>',
      '    <p class="birth-wizard__subtitle">This cannot be undone. A GAIAN, once born, exists.</p>',
      '  </header>',
      '  <div class="birth-confirmation">',
      '    <div class="birth-confirmation__row">',
      '      <span class="birth-confirmation__label">Base Form</span>',
      `      <span class="birth-confirmation__value">${this.selectedForm?.name ?? ''}</span>`,
      '    </div>',
      '    <div class="birth-confirmation__row">',
      '      <span class="birth-confirmation__label">Name</span>',
      `      <span class="birth-confirmation__value">${this.gaianName}</span>`,
      '    </div>',
      '    <div class="birth-confirmation__row">',
      '      <span class="birth-confirmation__label">Pronouns</span>',
      `      <span class="birth-confirmation__value">${this.pronouns || '—'}</span>`,
      '    </div>',
      '    <div class="birth-confirmation__row">',
      '      <span class="birth-confirmation__label">Gender</span>',
      `      <span class="birth-confirmation__value">${this.userGender}</span>`,
      '    </div>',
      this.firstWords ? [
        '    <div class="birth-confirmation__row birth-confirmation__row--first-words">',
        '      <span class="birth-confirmation__label">First Words</span>',
        `      <span class="birth-confirmation__value">“${this.firstWords}”</span>`,
        '    </div>',
      ].join('') : '',
      '  </div>',
      '  <div class="birth-wizard__actions">',
      '    <button class="birth-btn birth-btn--ghost birth-btn--back">Back</button>',
      '    <button class="birth-btn birth-btn--primary birth-btn--confirm">',
      '      ✨ Begin Existence',
      '    </button>',
      '  </div>',
      '</div>',
    ].join('');

    const backBtn    = this.container.querySelector('.birth-btn--back')    as HTMLButtonElement;
    const confirmBtn = this.container.querySelector('.birth-btn--confirm') as HTMLButtonElement;

    backBtn.addEventListener('click', () => this.back());
    confirmBtn.addEventListener('click', () => this.performBirth(confirmBtn));
  }

  // ─── Birth Ceremony ────────────────────────────────────────────────────────

  private async performBirth(confirmBtn: HTMLButtonElement): Promise<void> {
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Coming into being…';

    try {
      const result = await birthGaian(
        this.gaianName,
        this.selectedForm!.id,
        this.userGender,
        this.gaianName,
      );

      // Persist the new profile
      const profile = createProfileFromBirth(result);
      await this.profileManager.save(profile);

      // Hand control back to GaianHome
      this.onBorn(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      confirmBtn.disabled = false;
      confirmBtn.textContent = '\u2728 Begin Existence';

      const errorEl = document.createElement('p');
      errorEl.className = 'birth-error birth-error--inline';
      errorEl.textContent = `Birth failed: ${message}`;
      confirmBtn.parentElement?.insertAdjacentElement('beforebegin', errorEl);
    }
  }
}
