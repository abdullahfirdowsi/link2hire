/**
 * TypeScript interfaces matching backend models
 */

export enum WorkMode {
  REMOTE = 'Remote',
  ONSITE = 'On-site',
  HYBRID = 'Hybrid',
  UNKNOWN = 'Unknown'
}

export enum ConversationState {
  INITIAL = 'initial',
  AWAITING_CLARIFICATION = 'awaiting_clarification',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  ERROR = 'error'
}

export enum ClarificationChoice {
  COMBINED = 'combined',
  SEPARATE = 'separate'
}

export interface JobRole {
  title: string;
  description?: string;
}

export interface ExtractedJobData {
  company: string;
  roles: JobRole[];
  location: string;
  work_mode: WorkMode;
  experience: string;
  eligibility: string;
  salary?: string;
  apply_link: string;
  deadline?: string;
}

export interface LinkedInPost {
  post_text: string;
  hashtags: string[];
}

export interface ProcessingResponse {
  success: boolean;
  message: string;
  conversation_id: string;
  state: ConversationState;
  requires_clarification: boolean;
  clarification_message?: string;
  job_entries_created?: string[];
  linkedin_post?: LinkedInPost;
}

export interface JobProcessingRequest {
  raw_job_text: string;
  user_context?: any;
}

export interface ClarificationRequest {
  conversation_id: string;
  choice: ClarificationChoice;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
  linkedInPost?: LinkedInPost;
  requiresClarification?: boolean;
  conversationId?: string;
}
