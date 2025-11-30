import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { PlusCircle, History, LogOut } from 'lucide-react';

interface Session {
  id: number;
  theme: string;
  topic: string;
  timestamp: string;
  difficulty: string;
}

export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await api.get('/user/sessions');
        setSessions(response.data);
      } catch (err) {
        console.error(err);
        // If 401, redirect to login
        navigate('/');
      }
    };
    fetchSessions();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-slate-900">Student Dashboard</h1>
          <Button variant="ghost" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate('/exam')}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xl font-medium">Start New Exam</CardTitle>
              <PlusCircle className="h-6 w-6 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-sm text-slate-500">
                Begin a new speaking practice session based on your syllabus.
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-xl font-medium">History</CardTitle>
              <History className="h-6 w-6 text-slate-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{sessions.length}</div>
              <p className="text-xs text-slate-500">Completed Sessions</p>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Recent Activity</h2>
          {sessions.length === 0 ? (
            <p className="text-slate-500">No previous sessions found.</p>
          ) : (
            sessions.map((session) => (
              <Card key={session.id}>
                <CardHeader>
                  <div className="flex justify-between">
                    <div>
                      <CardTitle className="text-lg">{session.topic}</CardTitle>
                      <CardDescription>{session.theme}</CardDescription>
                    </div>
                    <div className="text-right text-sm text-slate-500">
                      <div>{new Date(session.timestamp).toLocaleDateString()}</div>
                      <div className="capitalize badge bg-slate-100 px-2 py-1 rounded mt-1 inline-block">{session.difficulty}</div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
