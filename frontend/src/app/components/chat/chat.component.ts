import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { JobService } from '../../services/job.service';
import {
  ChatMessage,
  ClarificationChoice,
  ConversationState,
  ProcessingResponse
} from '../../models/job.model';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef<HTMLTextAreaElement>;

  messages: ChatMessage[] = [];
  userInput: string = '';
  isProcessing: boolean = false;
  currentConversationId: string | null = null;
  awaitingClarification: boolean = false;
  private shouldScrollToBottom = false;

  constructor(private jobService: JobService) {}

  ngOnInit(): void {
    // Add welcome message
    this.addBotMessage(
      '👋 Welcome to Link2Hire! Paste your job posting text below and I\'ll help you process it.',
      false
    );
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  /**
   * Handle form submission
   */
  onSubmit(): void {
    if (!this.userInput.trim() || this.isProcessing) {
      return;
    }

    const input = this.userInput.trim();
    this.userInput = '';

    // Check if we're awaiting clarification
    if (this.awaitingClarification) {
      this.handleClarificationResponse(input);
    } else {
      this.processJobPosting(input);
    }
  }

  /**
   * Process job posting
   */
  private processJobPosting(jobText: string): void {
    // Add user message
    this.addUserMessage(jobText);

    // Add loading indicator
    this.isProcessing = true;
    const loadingMessage = this.addBotMessage('Processing your job posting...', true);

    // Call API
    this.jobService.processJob(jobText).subscribe({
      next: (response: ProcessingResponse) => {
        this.isProcessing = false;
        this.removeMessage(loadingMessage.id);
        this.handleProcessingResponse(response);
      },
      error: (error) => {
        this.isProcessing = false;
        this.removeMessage(loadingMessage.id);
        this.addBotMessage(
          `❌ Error: ${error.message}. Please try again.`,
          false
        );
      }
    });
  }

  /**
   * Handle processing response from API
   */
  private handleProcessingResponse(response: ProcessingResponse): void {
    this.currentConversationId = response.conversation_id;

    if (response.requires_clarification) {
      // Need clarification
      this.awaitingClarification = true;
      this.addBotMessage(response.clarification_message || '', false, {
        requiresClarification: true,
        conversationId: response.conversation_id
      });
    } else if (response.success && response.state === ConversationState.COMPLETED) {
      // Success - show results
      this.awaitingClarification = false;
      this.addBotMessage(response.message, false);
      
      // Show LinkedIn post if available
      if (response.linkedin_post) {
        this.addLinkedInPostMessage(response.linkedin_post);
      }
      
      // Add follow-up message
      setTimeout(() => {
        this.addBotMessage(
          'You can paste another job posting to process more jobs!',
          false
        );
      }, 500);
    } else {
      // Error or other state
      this.addBotMessage(
        response.message || 'Processing completed with unknown state.',
        false
      );
    }
  }

  /**
   * Handle clarification response
   */
  private handleClarificationResponse(response: string): void {
    const normalized = response.toLowerCase().trim();
    
    let choice: ClarificationChoice;
    if (normalized === 'combined' || normalized.includes('combined')) {
      choice = ClarificationChoice.COMBINED;
    } else if (normalized === 'separate' || normalized.includes('separate')) {
      choice = ClarificationChoice.SEPARATE;
    } else {
      this.addUserMessage(response);
      this.addBotMessage(
        'Please respond with "combined" or "separate".',
        false
      );
      return;
    }

    // Add user message
    this.addUserMessage(choice === ClarificationChoice.COMBINED ? 'Combined' : 'Separate');

    // Show loading
    this.isProcessing = true;
    this.awaitingClarification = false;
    const loadingMessage = this.addBotMessage('Processing your choice...', true);

    // Submit clarification
    if (!this.currentConversationId) {
      this.isProcessing = false;
      this.removeMessage(loadingMessage.id);
      this.addBotMessage('❌ Error: No active conversation.', false);
      return;
    }

    this.jobService.submitClarification(this.currentConversationId, choice).subscribe({
      next: (response: ProcessingResponse) => {
        this.isProcessing = false;
        this.removeMessage(loadingMessage.id);
        this.handleProcessingResponse(response);
      },
      error: (error) => {
        this.isProcessing = false;
        this.removeMessage(loadingMessage.id);
        this.addBotMessage(
          `❌ Error: ${error.message}. Please try again.`,
          false
        );
      }
    });
  }

  /**
   * Quick action buttons
   */
  onClarificationChoice(choice: 'combined' | 'separate'): void {
    if (this.isProcessing || !this.awaitingClarification) {
      return;
    }

    this.userInput = choice;
    this.onSubmit();
  }

  /**
   * Add user message
   */
  private addUserMessage(content: string): ChatMessage {
    const message: ChatMessage = {
      id: this.generateId(),
      type: 'user',
      content: content,
      timestamp: new Date()
    };
    this.messages.push(message);
    this.shouldScrollToBottom = true;
    return message;
  }

  /**
   * Add bot message
   */
  private addBotMessage(content: string, isLoading: boolean, extra?: any): ChatMessage {
    const message: ChatMessage = {
      id: this.generateId(),
      type: 'bot',
      content: content,
      timestamp: new Date(),
      isLoading: isLoading,
      ...extra
    };
    this.messages.push(message);
    this.shouldScrollToBottom = true;
    return message;
  }

  /**
   * Add LinkedIn post display message
   */
  private addLinkedInPostMessage(post: any): void {
    const message: ChatMessage = {
      id: this.generateId(),
      type: 'bot',
      content: '📝 Generated LinkedIn Post:',
      timestamp: new Date(),
      linkedInPost: post
    };
    this.messages.push(message);
    this.shouldScrollToBottom = true;
  }

  /**
   * Remove message by ID
   */
  private removeMessage(id: string): void {
    this.messages = this.messages.filter(m => m.id !== id);
  }

  /**
   * Clear chat
   */
  clearChat(): void {
    if (confirm('Are you sure you want to clear the chat?')) {
      this.messages = [];
      this.currentConversationId = null;
      this.awaitingClarification = false;
      this.isProcessing = false;
      this.ngOnInit();
    }
  }

  /**
   * Copy text to clipboard
   */
  copyToClipboard(text: string): void {
    navigator.clipboard.writeText(text).then(() => {
      // Could show a toast notification here
      console.log('Copied to clipboard');
    });
  }

  /**
   * Handle textarea auto-resize
   */
  onInputChange(): void {
    const textarea = this.messageInput?.nativeElement;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }

  /**
   * Scroll chat to bottom
   */
  private scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = 
        this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Handle Enter key (Shift+Enter for new line, Enter to submit)
   */
  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSubmit();
    }
  }
}
