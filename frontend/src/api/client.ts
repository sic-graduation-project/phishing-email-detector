import axios from "axios";
import type { InputKind, ScanRequest, ScanResult } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

// Shape of the /api/v1/analyze/{email,url,text} response, per the backend's
// Swagger docs (AnalysisResponse schema) at https://swagger-api.devanas.ly/.
interface AnalysisResponse {
  input_type: InputKind;
  classification: "Phishing" | "Legitimate";
  risk_score: number;
  reasons: string[];
}

interface ApiErrorBody {
  detail?: string;
}

const ANALYZE_ENDPOINTS: Record<InputKind, string> = {
  email: "/api/v1/analyze/email",
  url: "/api/v1/analyze/url",
  text: "/api/v1/analyze/text",
};

function buildPayload(request: ScanRequest): Record<string, unknown> {
  switch (request.kind) {
    case "email":
      return { subject: request.subject?.trim() || undefined, body: request.body };
    case "url":
      return { url: request.body };
    case "text":
      return { text: request.body };
  }
}

export async function scanEmail(request: ScanRequest): Promise<ScanResult> {
  try {
    const { data } = await http.post<AnalysisResponse>(
      ANALYZE_ENDPOINTS[request.kind],
      buildPayload(request)
    );

    return {
      id: crypto.randomUUID(),
      kind: data.input_type,
      verdict: data.classification === "Phishing" ? "phishing" : "safe",
      riskScore: data.risk_score,
      reasons: data.reasons,
      scannedAt: new Date().toISOString(),
      subject: request.subject,
      snippet: request.body.slice(0, 140),
    };
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = (err.response?.data as ApiErrorBody | undefined)?.detail;
      if (detail) throw new Error(detail);
      if (!err.response) {
        throw new Error("Unable to reach the analysis service. Please check your connection and try again.");
      }
    }
    throw new Error("Something went wrong while analyzing this content. Please try again.");
  }
}

export const inputKindLabel: Record<InputKind, string> = {
  email: "Email",
  url: "URL",
  text: "Text",
};
