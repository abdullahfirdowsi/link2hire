import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  ProcessingResponse,
  JobProcessingRequest,
  ClarificationRequest,
  ClarificationChoice
} from '../models/job.model';

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Process initial job posting request
   */
  processJob(rawJobText: string, userContext?: any): Observable<ProcessingResponse> {
    const request: JobProcessingRequest = {
      raw_job_text: rawJobText,
      user_context: userContext || {}
    };

    return this.http.post<ProcessingResponse>(
      `${this.apiUrl}/process-job`,
      request
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Submit clarification response
   */
  submitClarification(
    conversationId: string,
    choice: ClarificationChoice
  ): Observable<ProcessingResponse> {
    const request: ClarificationRequest = {
      conversation_id: conversationId,
      choice: choice
    };

    return this.http.post<ProcessingResponse>(
      `${this.apiUrl}/clarification-response`,
      request
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get conversation details
   */
  getConversation(conversationId: string): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/conversation/${conversationId}`
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Get job entries for conversation
   */
  getJobsByConversation(conversationId: string): Observable<any> {
    return this.http.get<any>(
      `${this.apiUrl}/jobs/${conversationId}`
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Check API health
   */
  checkHealth(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/health`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = error.error?.error || error.message || 'Server error';
    }

    console.error('API Error:', error);
    return throwError(() => new Error(errorMessage));
  }
}
