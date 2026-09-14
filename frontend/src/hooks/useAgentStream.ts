import { useCallback, useRef } from 'react';
import { usePortfolioStore } from '../store/usePortfolioStore';
import { FinalPortfolioPayload, PipelineStage } from '../types/portfolio';

const STAGE_MAP: Record<string, PipelineStage> = {
  'Ingestion Agent': 'ingestion',
  'Storyteller Agent': 'storyteller',
  'Design Agent': 'design',
  'Design & Layout Agent': 'design',
  'Portfolio Generator Agent': 'generator',
  'Reviewer Agent': 'reviewer',
};

export const useAgentStream = () => {
  const {
    targetRole,
    themePreference,
    selectedFile,
    setStatus,
    setActiveAgent,
    addLog,
    updateLastLogStatus,
    setPortfolio,
    setError,
    clearLogs,
  } = usePortfolioStore();

  const abortControllerRef = useRef<AbortController | null>(null);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setStatus('idle');
      setActiveAgent('Cancelled');
      addLog('System', 'Generation aborted by user.', 'error');
    }
  }, [setStatus, setActiveAgent, addLog]);

  const startStream = useCallback(async (overrideFile?: File) => {
    const fileToUpload = overrideFile || selectedFile;
    if (!fileToUpload) {
      setError('Please select or drop a resume PDF first.');
      return;
    }

    // Cancel any ongoing stream
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    clearLogs();
    setError(null);
    setStatus('uploading');
    setActiveAgent('Upload Manager');
    addLog('System', `Preparing upload: ${fileToUpload.name} (${(fileToUpload.size / 1024).toFixed(1)} KB)...`, 'running');

    const formData = new FormData();
    formData.append('file', fileToUpload);
    formData.append('target_role', targetRole || 'Full Stack Developer');
    if (themePreference) {
      formData.append('theme_preference', themePreference);
    }

    try {
      // Direct call with relative URL proxied by Vite or direct to port 8000
      const apiUrl = window.location.port === '3000' 
        ? '/api/generate-stream' 
        : 'http://localhost:8000/api/generate-stream';

      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server returned HTTP ${response.status}: ${errorText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null, cannot read SSE stream.');
      }

      updateLastLogStatus('completed');
      addLog('System', 'Connected to SSE pipeline. Running multi-agent swarm...', 'running');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentEvent = 'message';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        // Keep the last partial line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) {
            // End of SSE block, reset event
            currentEvent = 'message';
            continue;
          }

          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.replace('event:', '').trim();
          } else if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.replace('data:', '').trim();

            if (currentEvent === 'agent_status') {
              try {
                const parsed = JSON.parse(dataStr);
                const agent = parsed.agent || 'Agent';
                const message = parsed.message || '';
                
                updateLastLogStatus('completed');
                setActiveAgent(agent);
                if (STAGE_MAP[agent]) {
                  setStatus(STAGE_MAP[agent]);
                }
                addLog(agent, message, 'running');
              } catch (e) {
                console.error('Failed to parse agent_status data:', dataStr, e);
              }
            } else if (currentEvent === 'complete') {
              try {
                const finalPayload = JSON.parse(dataStr) as FinalPortfolioPayload;
                updateLastLogStatus('completed');
                addLog('Reviewer Agent', 'QA verification passed. Production portfolio payload rendered!', 'completed');
                setPortfolio(finalPayload);
                setStatus('completed');
                setActiveAgent('Pipeline Complete');
              } catch (e) {
                console.error('Failed to parse complete data:', dataStr, e);
                setError('Failed to parse completed portfolio data.');
                setStatus('error');
              }
            } else if (currentEvent === 'error') {
              try {
                const errData = JSON.parse(dataStr);
                const errorMsg = errData.error || 'Unknown error occurred in agent pipeline.';
                updateLastLogStatus('error');
                addLog('Error', errorMsg, 'error');
                setError(errorMsg);
                setStatus('error');
              } catch {
                setError(dataStr);
                setStatus('error');
              }
            }
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const msg = err instanceof Error ? err.message : 'Unknown streaming error';
      console.error('Stream generation error:', err);
      updateLastLogStatus('error');
      addLog('Stream Error', msg, 'error');
      setError(msg);
      setStatus('error');
    } finally {
      abortControllerRef.current = null;
    }
  }, [
    selectedFile,
    targetRole,
    themePreference,
    clearLogs,
    setError,
    setStatus,
    setActiveAgent,
    addLog,
    updateLastLogStatus,
    setPortfolio,
  ]);

  return {
    startStream,
    cancelStream,
    isStreaming: abortControllerRef.current !== null,
  };
};

