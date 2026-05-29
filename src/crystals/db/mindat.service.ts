/**
 * mindat.service.ts
 * Typed fetch wrapper for the Mindat API v1.
 *
 * Source: https://api.mindat.org/v1/
 * Docs:   https://api.mindat.org/schema/redoc/
 * Ref:    github.com/ChuBL/How-to-Use-Mindat-API
 *
 * Requires a Mindat API token — obtain free at:
 * https://www.mindat.org/a/how_to_get_my_mindat_api_key
 *
 * Set MINDAT_API_KEY in your environment or Tauri config.
 */

import type { MindatMineral } from './crystal.schema';

// ── Constants ──────────────────────────────────────────────────────────────

const MINDAT_BASE_URL = 'https://api.mindat.org/v1';

/**
 * Core fields we request from Mindat.
 * Keeping this explicit reduces response payload size.
 * Full field list: api.mindat.org/schema/redoc/#operation/minerals_list
 */
const MINDAT_FIELDS = [
  'id', 'longid', 'guid', 'name',
  'ima_formula', 'mindat_formula', 'ima_status', 'ima_year',
  'strunzten', 'dana8ed',
  'crystal_system',
  'hardness_min', 'hardness_max',
  'specific_gravity_min', 'specific_gravity_max',
  'cleavage', 'fracture', 'tenacity',
  'luster', 'diaphaneity',
  'colour', 'streak', 'fluorescence',
  'ri_min', 'ri_max', 'birefringence', 'optical_type',
  'shortdesc', 'updttime',
].join(',');

// ── Types ──────────────────────────────────────────────────────────────────

export interface MindatListResponse {
  count:    number;
  next:     string | null;
  previous: string | null;
  results:  MindatMineral[];
}

export interface MindatServiceConfig {
  /** Mindat API token. Falls back to import.meta.env.VITE_MINDAT_API_KEY */
  apiKey?: string;
  /** Override base URL (useful for testing) */
  baseUrl?: string;
}

// ── Service Class ──────────────────────────────────────────────────────────

export class MindatService {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor(config: MindatServiceConfig = {}) {
    this.baseUrl = config.baseUrl ?? MINDAT_BASE_URL;
    this.apiKey  = config.apiKey
      ?? (typeof import.meta !== 'undefined'
          ? (import.meta as any).env?.VITE_MINDAT_API_KEY
          : undefined)
      ?? '';

    if (!this.apiKey) {
      console.warn(
        '[MindatService] No API key set. '
        + 'Get yours free at https://www.mindat.org/a/how_to_get_my_mindat_api_key '
        + 'then set VITE_MINDAT_API_KEY in your .env'
      );
    }
  }

  // ── Private helpers ──────────────────────────────────────────────────────

  private headers(): HeadersInit {
    return {
      'Authorization': `Token ${this.apiKey}`,
      'Content-Type':  'application/json',
      'Accept':        'application/json',
    };
  }

  private async get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

    const res = await fetch(url.toString(), {
      method:  'GET',
      headers: this.headers(),
    });

    if (!res.ok) {
      throw new Error(
        `[MindatService] ${res.status} ${res.statusText} — GET ${url.toString()}`
      );
    }

    return res.json() as Promise<T>;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /**
   * Fetch a single mineral by its Mindat integer ID.
   * Example: getById(1451) → Amethyst
   */
  async getById(id: number): Promise<MindatMineral> {
    return this.get<MindatMineral>(`/minerals/${id}/`, { fields: MINDAT_FIELDS });
  }

  /**
   * Search minerals by name (case-insensitive, partial match).
   * Returns the first page of results.
   */
  async searchByName(
    name: string,
    options: { page?: number; pageSize?: number } = {}
  ): Promise<MindatListResponse> {
    const params: Record<string, string> = {
      name:      name,
      fields:    MINDAT_FIELDS,
      page_size: String(options.pageSize ?? 10),
    };
    if (options.page) params.page = String(options.page);
    return this.get<MindatListResponse>('/minerals/', params);
  }

  /**
   * Fetch minerals by IMA-approved status.
   * ima_status = 'A' returns only IMA-approved minerals.
   */
  async getImaApproved(
    options: { page?: number; pageSize?: number } = {}
  ): Promise<MindatListResponse> {
    const params: Record<string, string> = {
      ima_status: 'A',
      fields:     MINDAT_FIELDS,
      page_size:  String(options.pageSize ?? 20),
    };
    if (options.page) params.page = String(options.page);
    return this.get<MindatListResponse>('/minerals/', params);
  }

  /**
   * Fetch minerals by crystal system.
   */
  async getByCrystalSystem(
    system: MindatMineral['crystal_system'],
    options: { page?: number; pageSize?: number } = {}
  ): Promise<MindatListResponse> {
    if (!system) throw new Error('crystal_system is required');
    const params: Record<string, string> = {
      crystal_system: system,
      fields:         MINDAT_FIELDS,
      page_size:      String(options.pageSize ?? 20),
    };
    if (options.page) params.page = String(options.page);
    return this.get<MindatListResponse>('/minerals/', params);
  }

  /**
   * Fetch minerals within a Mohs hardness range.
   */
  async getByHardness(
    min: number,
    max: number,
    options: { page?: number; pageSize?: number } = {}
  ): Promise<MindatListResponse> {
    const params: Record<string, string> = {
      hardness_min__gte: String(min),
      hardness_max__lte: String(max),
      fields:            MINDAT_FIELDS,
      page_size:         String(options.pageSize ?? 20),
    };
    if (options.page) params.page = String(options.page);
    return this.get<MindatListResponse>('/minerals/', params);
  }

  /**
   * Fetch the next page from a paginated Mindat list response.
   * Pass the `next` URL returned by a previous call.
   */
  async getNextPage(nextUrl: string): Promise<MindatListResponse> {
    const res = await fetch(nextUrl, {
      method:  'GET',
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(
        `[MindatService] ${res.status} ${res.statusText} — GET ${nextUrl}`
      );
    }
    return res.json() as Promise<MindatListResponse>;
  }

  /**
   * Build the canonical Mindat URL for a mineral by name slug.
   * Useful for deep-linking to Mindat from the GAIA-OS crystal viewer.
   */
  static mineralUrl(nameSlug: string): string {
    return `https://www.mindat.org/min-${nameSlug.toLowerCase().replace(/\s+/g, '')}.html`;
  }
}

// ── Default singleton ──────────────────────────────────────────────────────

/** Pre-configured singleton. Import and use directly. */
export const mindatService = new MindatService();
