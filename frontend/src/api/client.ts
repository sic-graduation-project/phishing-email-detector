import axios from "axios";
import type { InputKind, ScanRequest, ScanResult } from "../types";
//inputkind :Email URL Text
// ScanRequest : kind: InputKind; subject?: string; body: string;
/* ScanResult
  id: "...",
  kind: "email",
  verdict: "phishing",
  riskScore: 85,
  reasons: [...]
*/
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const http = axios.create({
  baseURL: API_BASE_URL,
  // Render's free service can take about a minute to wake after inactivity.
  timeout: 90000,
});
//الملف هذا حلقت وصل بين الفرونت و الباك
// Shape of the /api/v1/analyze/{email,url,text} response, per the backend's
// Swagger docs (AnalysisResponse schema) at https://swagger-api.devanas.ly/.
interface AnalysisResponse {
  input_type: InputKind;
  classification: "Phishing" | "Legitimate";
  risk_score: number;
  reasons: string[];
}// how respones look like in backend when we send request to analyze email or url or text

interface ApiErrorBody {
  detail?: string;
}

const ANALYZE_ENDPOINTS: Record<InputKind, string> = {
  email: "/api/v1/analyze/email",
  url: "/api/v1/analyze/url",
  text: "/api/v1/analyze/text",
};//إذا النوع: email استخدم: /api/v1/analyze/email

function buildPayload(request: ScanRequest): Record<string, unknown> {
  switch (request.kind) {
    case "email":
      return {
        sender: request.sender?.trim() || undefined,
        subject: request.subject?.trim() || undefined,
        body: request.body,
      };
    case "url":
      return { url: request.body };
    case "text":
      return { text: request.body };
  }
}

export async function scanEmail(request: ScanRequest): Promise<ScanResult> {
  try {
    const { data } = await http.post<AnalysisResponse>(//انتظار الباك حتى يرد على الطلب
      ANALYZE_ENDPOINTS[request.kind],
      buildPayload(request)
    );

    return {
      id: crypto.randomUUID(),
      kind: data.input_type,
      verdict: data.classification === "Phishing" ? "phishing" : "safe",
      riskScore: data.risk_score,//هنا نسجل النتيجة التي اعطاها الباك
      reasons: data.reasons,//هنا نسجل الاسباب التي جعلت الباك يقرر ان هذا البريد او الرابط او النص مشبوه
      scannedAt: new Date().toISOString(),//هنا نسجل الوقت الذي استلم فيه الفرونت النتيجة من الباك
      subject: request.subject,//هنا نسجل الموضوع الذي ارسله المستخدم في الفرونت
      snippet: request.body.slice(0, 140),
    };
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = (err.response?.data as ApiErrorBody | undefined)?.detail;
      if (detail) throw new Error(detail);//هنا اذا الباك رد برسالة خطأ نعرضها للمستخدم
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
