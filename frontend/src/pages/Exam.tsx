import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/card';
import { Mic, Square, Play, ArrowLeft, CheckCircle, Loader2 } from 'lucide-react';

interface Theme {
  theme: string;
  topics: { name: string, subtopics: string[] }[];
}

interface AnalysisResult {
  original_question_english: string;
  transcription: string;
  translation: string;
  score: number;
  feedback: string;
}

export default function Exam() {
  const navigate = useNavigate();
  const [step, setStep] = useState<'config' | 'question' | 'recording' | 'analyzing' | 'result'>('config');
  const [themes, setThemes] = useState<Theme[]>([]);
  
  // Config State
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [difficulty, setDifficulty] = useState('easy');

  // Exam State
  const [questionText, setQuestionText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.get('/config');
        setThemes(response.data.themes);
      } catch (err) {
        console.error(err);
      }
    };
    fetchConfig();
  }, []);

  const handleGenerate = async () => {
    if (!selectedTheme || !selectedTopic) return;
    setStep('question');
    try {
      const response = await api.post('/generate', {
        theme: selectedTheme,
        topic: selectedTopic,
        difficulty,
        language: 'Russian'
      });
      
      setQuestionText(response.data.question_text);
      setSessionId(response.data.session_id);
      
      // Convert base64 to blob url
      const byteCharacters = atob(response.data.audio_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      
      // Auto play
      setTimeout(() => {
        if (audioRef.current) audioRef.current.play();
      }, 500);

    } catch (err) {
      console.error(err);
      setStep('config');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      setAudioChunks([]);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          setAudioChunks((prev) => [...prev, e.data]);
        }
      };

      recorder.start();
      setRecording(true);
      setStep('recording');
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && recording) {
      mediaRecorder.stop();
      setRecording(false);
      setStep('analyzing');
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await submitResponse(audioBlob);
      };
    }
  };

  const submitResponse = async (audioBlob: Blob) => {
    if (!sessionId) return;
    
    const formData = new FormData();
    formData.append('session_id', sessionId.toString());
    formData.append('audio_file', audioBlob, 'response.wav');
    formData.append('original_question', questionText);
    formData.append('theme_context', `${selectedTheme} - ${selectedTopic}`);
    formData.append('target_language', 'Russian');

    try {
      const response = await api.post('/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
      setStep('result');
    } catch (err) {
      console.error(err);
      alert("Analysis failed.");
      setStep('config');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 flex items-center justify-center">
      <div className="w-full max-w-2xl">
        <Button variant="ghost" onClick={() => navigate('/dashboard')} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
        </Button>

        {/* CONFIGURATION STEP */}
        {step === 'config' && (
          <Card>
            <CardHeader>
              <CardTitle>Configure Exam Session</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Theme</label>
                <select 
                  className="w-full p-2 border rounded-md"
                  value={selectedTheme}
                  onChange={(e) => { setSelectedTheme(e.target.value); setSelectedTopic(''); }}
                >
                  <option value="">Select a Theme...</option>
                  {themes.map(t => (
                    <option key={t.theme} value={t.theme}>{t.theme}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Topic</label>
                <select 
                  className="w-full p-2 border rounded-md"
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  disabled={!selectedTheme}
                >
                  <option value="">Select a Topic...</option>
                  {themes.find(t => t.theme === selectedTheme)?.topics.map(topic => (
                    <option key={topic.name} value={topic.name}>{topic.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Difficulty</label>
                <select 
                  className="w-full p-2 border rounded-md"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full" onClick={handleGenerate} disabled={!selectedTheme || !selectedTopic}>
                Start Session
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* QUESTION STEP */}
        {step === 'question' && (
          <Card>
            <CardHeader>
              <CardTitle>Listen to the Question</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center space-y-6 py-8">
              <div className="p-4 bg-blue-50 rounded-full">
                <Play className="h-12 w-12 text-blue-600" />
              </div>
              <audio ref={audioRef} src={audioUrl} controls className="w-full" />
              <p className="text-sm text-slate-500 text-center">
                Listen carefully. When you are ready, press record to answer.
              </p>
            </CardContent>
            <CardFooter>
              <Button className="w-full" size="lg" onClick={startRecording}>
                <Mic className="mr-2 h-5 w-5" /> Start Recording Answer
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* RECORDING STEP */}
        {step === 'recording' && (
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="text-red-600 animate-pulse">Recording...</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center py-12">
              <div className="h-24 w-24 rounded-full bg-red-100 flex items-center justify-center animate-ping">
                <Mic className="h-10 w-10 text-red-600" />
              </div>
            </CardContent>
            <CardFooter>
              <Button variant="destructive" className="w-full" size="lg" onClick={stopRecording}>
                <Square className="mr-2 h-5 w-5" /> Stop & Submit
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* ANALYZING STEP */}
        {step === 'analyzing' && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="text-lg font-medium text-slate-700">Analyzing your response...</p>
              <p className="text-sm text-slate-500">Checking grammar, pronunciation, and relevance.</p>
            </CardContent>
          </Card>
        )}

        {/* RESULT STEP */}
        {step === 'result' && result && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Assessment Results</CardTitle>
                <div className={`text-2xl font-bold ${result.score >= 7 ? 'text-green-600' : result.score >= 4 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {result.score}/10
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-slate-50 p-4 rounded-lg space-y-2">
                <h3 className="font-medium text-slate-900">Question</h3>
                <p className="text-slate-700 italic">"{questionText}"</p>
                <p className="text-sm text-slate-500">{result.original_question_english}</p>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium text-slate-900">Your Answer</h3>
                <p className="text-slate-700">{result.transcription || "(No speech detected)"}</p>
                <p className="text-sm text-slate-500">{result.translation}</p>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h3 className="font-medium text-blue-900 flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2" /> Feedback
                </h3>
                <p className="text-blue-800 text-sm mt-1">{result.feedback}</p>
              </div>
            </CardContent>
            <CardFooter className="flex gap-2">
              <Button variant="outline" className="w-full" onClick={() => setStep('config')}>
                New Session
              </Button>
              <Button className="w-full" onClick={() => setStep('question')}>
                Retry Question
              </Button>
            </CardFooter>
          </Card>
        )}
      </div>
    </div>
  );
}
