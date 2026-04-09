import React, { useState, useEffect } from 'react';
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  ExternalLink,
  MessageSquare,
  Settings,
  MoreVertical,
  CheckCircle2,
  X,
  LayoutDashboard,
  Shield,
  Eye,
  FileText,
  Copy,
  Check,
  MessageSquareText,
  AlertCircle,
  Activity,
  Database,
  Key,
  Code,
  PanelLeftClose,
  PanelLeftOpen,
  FlaskConical,
  Zap,
  Terminal,
  SendHorizontal,
  Loader2,
  Briefcase,
  GitBranch,
  BookOpen,
  Globe,
  Trash,
  PlusCircle,
  Settings2,
  Lock,
  User,
  LogOut,
  ArrowRight,
  History,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

const App = () => {
  // Estados de Autenticação e Navegação
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginData, setLoginData] = useState({ username: '', password: '' });

  // Estados do Dashboard
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [modalMode, setModalMode] = useState('create');
  const [reportTab, setReportTab] = useState('message');
  const [copied, setCopied] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isTesting, setIsTesting] = useState(false);
  const [confirmDisparo, setConfirmDisparo] = useState(false);
  const [confirmCountdown, setConfirmCountdown] = useState(10);
  const [testHistory, setTestHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [expandedHistory, setExpandedHistory] = useState(null);
  const [historyDetailTab, setHistoryDetailTab] = useState('message');
  const [historyFullView, setHistoryFullView] = useState(null);

  useEffect(() => {
    if (!confirmDisparo) return;
    setConfirmCountdown(10);
    const interval = setInterval(() => {
      setConfirmCountdown(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          setConfirmDisparo(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [confirmDisparo]);

  const initialFormState = {
    id: null,
    name: '',
    whatsapp: '',
    url: 'http://localhost:31000',
    apiToken: '',
    sgaUser: '',
    sgaPass: '',
    quepasaToken: '319f5001-82c5-46ab-a900-0a4d0b17bc79',
    isActive: true,
    lastReport: '',
    technicalLog: '',
    integrationConfig: {
      scheduler: "0 9 * * *",
      filter: "hinova.status == 'confirmed'",
      retry_policy: "max_attempts: 3",
      webhook: "active",
      format: "BRL"
    },
    businessRules: [
      "Disparo automático configurado para às 09:00 AM.",
      "Filtrar apenas vendas confirmadas no Hinova.",
      "Não enviar se houver pendência financeira crítica.",
      "Incluir resumo de ativos e cancelados do dia anterior."
    ],
    stats: {
      db_sync_count: 0,
      hinova_auth_count: 0,
      system_fails: 0
    }
  };

  const API_BASE = 'http://localhost:8000';

  const [formData, setFormData] = useState(initialFormState);
  const [tenants, setTenants] = useState([]);

  const fetchTenants = async () => {
    try {
      const res = await fetch(`${API_BASE}/tenants/`);
      const data = await res.json();
      setTenants(data.map(t => ({
        id: t.id,
        name: t.nome,
        whatsapp: t.whatsapp_destino,
        url: t.quepasa_base_url,
        isActive: t.ativo,
        lastSend: t.ultimo_envio ? new Date(t.ultimo_envio).toLocaleString('pt-BR') : 'Nunca',
        status: t.ultimo_status || 'pending',
        lastReport: '',
        technicalLog: '',
        businessRules: [
          "Disparo automático configurado para às 16:30.",
          "Filtrar apenas vendas confirmadas no Hinova.",
          "Incluir resumo de ativos e cancelados do dia."
        ],
        stats: { db_sync_count: 0, hinova_auth_count: 0, system_fails: 0 }
      })));
    } catch (err) {
      console.error('Erro ao carregar tenants:', err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) fetchTenants();
  }, [isAuthenticated]);

  // Lógica de Login
  const [loginError, setLoginError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setLoginError('');
    setTimeout(() => {
      if (loginData.username === 'Atomos' && loginData.password === 'atomos_1234') {
        setIsAuthenticated(true);
      } else {
        setLoginError('Usuário ou senha incorretos.');
        setTimeout(() => setLoginError(''), 4000);
      }
      setIsLoggingIn(false);
    }, 1200);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setLoginData({ username: '', password: '' });
  };

  // Funções do Dashboard
  const handleOpenCreate = () => {
    setModalMode('create');
    setFormData(initialFormState);
    setIsModalOpen(true);
    setIsClosing(false);
    setIsSidebarOpen(true);
  };

  const handleOpenEdit = async (tenant) => {
    setModalMode('edit');
    setFormData({ ...tenant });
    setIsModalOpen(true);
    setIsClosing(false);
    setIsSidebarOpen(true);
    try {
      const res = await fetch(`${API_BASE}/tenants/${tenant.id}/detalhe`);
      if (res.ok) {
        const d = await res.json();
        setFormData(prev => ({
          ...prev,
          name: d.nome,
          apiToken: d.hinova_token,
          sgaUser: d.hinova_usuario,
          sgaPass: d.hinova_senha,
          quepasaToken: d.quepasa_token,
          url: d.quepasa_base_url,
          whatsapp: d.whatsapp_destino,
          isActive: d.ativo,
        }));
      }
    } catch (err) {
      console.error('Erro ao carregar detalhes:', err);
    }
  };

  const fetchHistory = async (tenantId) => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_BASE}/tenants/${tenantId}/historico`);
      if (res.ok) {
        setTestHistory(await res.json());
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleOpenReport = (tenant) => {
    setModalMode('report');
    setFormData({ ...tenant });
    setIsModalOpen(true);
    setIsClosing(false);
    setIsSidebarOpen(true);
    setReportTab('message');
    setExpandedHistory(null);
    fetchHistory(tenant.id);
  };

  const handleSave = async (e) => {
    if (e) e.preventDefault();
    if (modalMode === 'report') {
      closeModal();
      return;
    }
    try {
      if (modalMode === 'create') {
        const payload = {
          nome: formData.name,
          hinova_token: formData.apiToken,
          hinova_usuario: formData.sgaUser,
          hinova_senha: formData.sgaPass,
          quepasa_token: formData.quepasaToken,
          quepasa_base_url: formData.url,
          whatsapp_destino: formData.whatsapp,
        };
        const res = await fetch(`${API_BASE}/tenants/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json();
          alert('Erro ao criar: ' + (err.detail || JSON.stringify(err)));
          return;
        }
      } else {
        const payload = {
          nome: formData.name,
          hinova_token: formData.apiToken || undefined,
          hinova_usuario: formData.sgaUser || undefined,
          hinova_senha: formData.sgaPass || undefined,
          quepasa_token: formData.quepasaToken || undefined,
          quepasa_base_url: formData.url || undefined,
          whatsapp_destino: formData.whatsapp || undefined,
          ativo: formData.isActive,
        };
        const res = await fetch(`${API_BASE}/tenants/${formData.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json();
          alert('Erro ao atualizar: ' + (err.detail || JSON.stringify(err)));
          return;
        }
      }
      await fetchTenants();
      closeModal();
    } catch (err) {
      alert('Erro de conexão: ' + err.message);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Tem certeza que deseja excluir este tenant?')) {
      try {
        await fetch(`${API_BASE}/tenants/${id}`, { method: 'DELETE' });
        await fetchTenants();
      } catch (err) {
        alert('Erro ao excluir: ' + err.message);
      }
    }
  };

  const handleAddRule = () => {
    setFormData({
      ...formData,
      businessRules: [...formData.businessRules, "Nova diretriz de negócio..."]
    });
  };

  const handleRemoveRule = (index) => {
    const newRules = formData.businessRules.filter((_, i) => i !== index);
    setFormData({ ...formData, businessRules: newRules });
  };

  const handleUpdateRule = (index, value) => {
    const newRules = [...formData.businessRules];
    newRules[index] = value;
    setFormData({ ...formData, businessRules: newRules });
  };

  const handleCopyReport = () => {
    const textToCopy = reportTab === 'logs' ? formData.technicalLog : formData.lastReport;
    const el = document.createElement('textarea');
    el.value = textToCopy;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const [operationType, setOperationType] = useState(null); // 'test' | 'send'
  const [elapsedTime, setElapsedTime] = useState(0);
  const [abortController, setAbortController] = useState(null);

  useEffect(() => {
    let interval;
    if (isTesting) {
      setElapsedTime(0);
      interval = setInterval(() => setElapsedTime(prev => prev + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isTesting]);

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const addLog = (msg, type = 'INFO') => {
    const now = new Date().toLocaleString('pt-BR');
    const prefix = type === 'ERROR' ? '❌' : type === 'SUCCESS' ? '✅' : 'ℹ️';
    const line = `${now} [${type}] ${prefix} ${msg}`;
    setFormData(prev => ({
      ...prev,
      technicalLog: prev.technicalLog ? prev.technicalLog + '\n' + line : line
    }));
  };

  const addSeparator = () => {
    setFormData(prev => ({
      ...prev,
      technicalLog: prev.technicalLog ? prev.technicalLog + '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' : ''
    }));
  };

  const clearLogs = () => {
    setFormData(prev => ({ ...prev, technicalLog: '' }));
  };

  const handleCancel = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
    setIsTesting(false);
    setOperationType(null);
    if (operationType === 'send') {
      addLog('Aguarde cancelado no frontend — se o backend já estava enviando, a mensagem pode ter sido entregue.', 'ERROR');
    } else {
      addLog('Operação cancelada pelo usuário.', 'ERROR');
    }
  };

  const runPipeline = async (endpoint, successMsg, opType) => {
    if (!formData.id) return;
    const controller = new AbortController();
    setAbortController(controller);
    setIsTesting(true);
    setOperationType(opType);
    addSeparator();
    addLog(opType === 'test' ? 'Iniciando teste / verificação de dados...' : 'Iniciando disparo para WhatsApp...');
    try {
      const res = await fetch(`${API_BASE}/tenants/${formData.id}/${endpoint}`, {
        method: 'POST',
        signal: controller.signal,
      });
      const data = await res.json();
      if (data.logs) {
        setFormData(prev => ({
          ...prev,
          technicalLog: prev.technicalLog ? prev.technicalLog + '\n' + data.logs : data.logs
        }));
      }
      if (res.ok && data.sucesso) {
        if (opType === 'test' && data.mensagem) {
          setFormData(prev => ({ ...prev, lastReport: data.mensagem }));
          setReportTab('message');
          addLog('Teste concluído! Preview da mensagem atualizado.', 'SUCCESS');
        } else {
          addLog(successMsg, 'SUCCESS');
        }
        await fetchTenants();
      } else {
        addLog(data.mensagem || data.detail || 'Falha na operação.', 'ERROR');
      }
      if (opType === 'test') fetchHistory(formData.id);
    } catch (err) {
      if (err.name === 'AbortError') return;
      addLog('Erro de conexão com o backend: ' + err.message, 'ERROR');
    } finally {
      setIsTesting(false);
      setOperationType(null);
      setAbortController(null);
    }
  };

  const handleTest = () => runPipeline('testar', 'Teste concluído!', 'test');

  const handleSendRequest = () => {
    if (!formData.lastReport) {
      addLog('Rode o teste primeiro para gerar a mensagem.', 'ERROR');
      return;
    }
    setConfirmDisparo(true);
  };

  const handleSendConfirm = async () => {
    setConfirmDisparo(false);
    const controller = new AbortController();
    setAbortController(controller);
    setIsTesting(true);
    setOperationType('send');
    addSeparator();
    addLog('Enviando mensagem para WhatsApp...');
    try {
      const res = await fetch(`${API_BASE}/tenants/${formData.id}/disparar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensagem: formData.lastReport }),
        signal: controller.signal,
      });
      const data = await res.json();
      if (data.logs) {
        setFormData(prev => ({
          ...prev,
          technicalLog: prev.technicalLog ? prev.technicalLog + '\n' + data.logs : data.logs
        }));
      }
      if (res.ok && data.sucesso) {
        addLog('Relatório enviado com sucesso para WhatsApp!', 'SUCCESS');
        await fetchTenants();
      } else {
        addLog(data.mensagem || data.detail || 'Falha no envio.', 'ERROR');
      }
    } catch (err) {
      if (err.name === 'AbortError') return;
      addLog('Erro de conexão: ' + err.message, 'ERROR');
    } finally {
      setIsTesting(false);
      setOperationType(null);
      setAbortController(null);
    }
  };

  const closeModal = () => {
    if (isClosing) return;
    setIsClosing(true);
    setTimeout(() => {
      setIsModalOpen(false);
      setIsClosing(false);
    }, 500);
  };

  const getInputStyle = (value) => {
    const base = "w-full border-2 rounded-[2rem] px-8 py-4 outline-none transition-all duration-500 text-sm font-bold";
    return value ? `${base} bg-[#F3F8F4]/80 border-[#244235]/30 text-[#244235] shadow-lg shadow-[#244235]/5` : `${base} bg-white border-[#718878]/10 text-[#111A17]`;
  };

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && confirmDisparo) {
        setConfirmDisparo(false);
        return;
      }
      if (event.key === 'Escape' && isModalOpen) {
        closeModal();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isModalOpen, isClosing, confirmDisparo]);

  const actionBtnBase = "w-14 h-14 flex items-center justify-center rounded-2xl transition-all duration-300 active:scale-90 shadow-sm hover:shadow-xl";

  // RENDERIZAÇÃO DA TELA DE LOGIN
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center relative bg-[#111A17] font-sans overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 z-0 opacity-20">
          <svg className="w-full h-full">
            <filter id="noise">
              <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
            </filter>
            <rect width="100%" height="100%" filter="url(#noise)" />
          </svg>
        </div>
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#244235] rounded-full blur-[120px] opacity-20 animate-pulse" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-[#244235] rounded-full blur-[120px] opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />

        <div className="relative z-10 w-full max-w-lg p-8 animate-in fade-in zoom-in duration-700">
          <div className="bg-white/5 backdrop-blur-2xl rounded-[3.5rem] border border-white/10 p-10 shadow-[0_40px_80px_-15px_rgba(0,0,0,0.5)] text-center">
            <div className="mb-12">
              <h1 className="text-3xl font-black text-white tracking-[0.2em] uppercase mb-2 pt-4">Atomos API</h1>
              <p className="text-[#718878] text-[10px] font-bold uppercase tracking-[0.4em]">Autenticação de Segurança</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div className="relative group">
                <div className="absolute inset-y-0 left-6 flex items-center text-[#718878] group-focus-within:text-[#244235] transition-colors">
                  <User size={18} />
                </div>
                <input
                  type="text"
                  placeholder="Utilizador"
                  className="w-full bg-white/5 border-2 border-white/10 rounded-[2rem] pl-16 pr-8 py-5 text-white font-bold outline-none focus:border-white/60 transition-all placeholder:text-white/20"
                  value={loginData.username}
                  onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                  required
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-6 flex items-center text-[#718878] group-focus-within:text-[#244235] transition-colors">
                  <Lock size={18} />
                </div>
                <input
                  type="password"
                  placeholder="Palavra-passe"
                  className="w-full bg-white/5 border-2 border-white/10 rounded-[2rem] pl-16 pr-8 py-5 text-white font-bold outline-none focus:border-white/60 transition-all placeholder:text-white/20"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  required
                />
              </div>

              {loginError && (
                <p className="text-rose-500 text-xs font-bold text-center animate-pulse">{loginError}</p>
              )}

              <button
                type="submit"
                disabled={isLoggingIn}
                className="w-full bg-[#F3F8F4] text-[#111A17] font-black uppercase text-xs tracking-[0.3em] py-6 rounded-[2rem] shadow-2xl hover:bg-[#244235] hover:text-white transition-all duration-500 active:scale-95 flex items-center justify-center gap-3 mt-10"
              >
                {isLoggingIn ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <>
                    Entrar no Sistema
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>

            <p className="text-center mt-10 text-[9px] font-black text-[#718878] uppercase tracking-[0.2em] opacity-40">
              © 2026 Atomos Infrastructure v2.5
            </p>
          </div>
        </div>
      </div>
    );
  }

  // RENDERIZAÇÃO DO DASHBOARD
  return (
    <div className="min-h-screen relative bg-[#F3F8F4] font-sans text-[#111A17] overflow-x-hidden animate-in fade-in duration-1000">

      {/* Wall Texture Effect */}
      <svg className="absolute w-0 h-0 overflow-hidden pointer-events-none">
        <filter id="blurredWallTexture">
          <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="6" result="noise" />
          <feDiffuseLighting in="noise" lightingColor="#F3F8F4" surfaceScale="5" result="light">
            <feDistantLight azimuth="45" elevation="40" />
          </feDiffuseLighting>
          <feGaussianBlur in="light" stdDeviation="1.8" />
        </filter>
      </svg>
      <div className="fixed inset-0 pointer-events-none z-0 scale-105" style={{ filter: 'url(#blurredWallTexture)', backgroundColor: '#E9EFEA' }} />

      <nav className="relative z-20 bg-[#111A17] text-[#F3F8F4] px-8 py-5 flex justify-between items-center shadow-2xl">
        <div className="flex items-center gap-4">
          <h1 className="text-sm font-black tracking-[0.3em] uppercase italic leading-none">API Busca Lucas</h1>
        </div>
        <button onClick={handleLogout} className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-[#718878] hover:text-white transition-colors group">
          Sair <LogOut size={14} className="group-hover:translate-x-1 transition-transform" />
        </button>
      </nav>

      <main className="relative z-10 max-w-6xl mx-auto p-4 sm:p-10">
        <div className="bg-white/40 backdrop-blur-[40px] rounded-[4rem] border border-white/50 p-8 sm:p-14 shadow-[0_60px_120px_-30px_rgba(36,66,53,0.15)] ring-1 ring-[#244235]/5">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-10">
            <div>
              <div className="px-4 py-1.5 bg-[#244235] text-[#F3F8F4] text-[10px] font-bold uppercase tracking-[0.2em] rounded-xl inline-block mb-3 shadow-xl">Gestão</div>
              <h2 className="text-3xl font-bold text-[#111A17] tracking-tight leading-none mb-3">Meus Clientes</h2>
              <p className="text-[#718878] font-medium text-base opacity-90 max-w-lg italic">Administre as instâncias e acompanhe os relatórios diários de performance.</p>
            </div>
            <button onClick={handleOpenCreate} className="group relative flex items-center bg-[#244235] text-white h-16 w-16 hover:w-52 rounded-full font-bold transition-all duration-500 shadow-2xl overflow-hidden active:scale-95">
              <div className="flex items-center justify-center min-w-[64px]"><Plus size={24} strokeWidth={3} /></div>
              <span className="opacity-0 group-hover:opacity-100 whitespace-nowrap pr-8 text-xs uppercase tracking-[0.2em] transition-opacity duration-300">Novo Cliente</span>
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6">
            {tenants.map((tenant) => (
              <div key={tenant.id} className="bg-white/95 rounded-[3.5rem] border border-[#718878]/5 py-12 px-10 shadow-sm hover:shadow-2xl transition-all duration-700 border-l-[12px] border-l-[#244235] group">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-8">
                  <div className="flex-1">
                    <h3 className="text-3xl font-bold text-[#111A17] tracking-tight group-hover:translate-x-1 transition-transform duration-500">{tenant.name}</h3>
                    <div className="flex flex-wrap gap-4 mt-6">
                      <div className="flex items-center gap-2 text-[#111A17] font-bold text-xs bg-[#F3F8F4] px-4 py-2 rounded-xl border border-[#244235]/5 shadow-inner">
                        <MessageSquare size={16} className="text-[#244235]" /> {tenant.whatsapp}
                      </div>
                      <span className={`px-4 py-2 rounded-xl text-[9px] font-bold tracking-widest uppercase flex items-center gap-2 border ${tenant.isActive ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-gray-100 text-gray-400 border-gray-200'}`}>
                        <div className={`h-1.5 w-1.5 rounded-full ${tenant.isActive ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'}`} />
                        {tenant.isActive ? 'Ativo' : 'Inativo'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button onClick={() => handleOpenReport(tenant)} className={`${actionBtnBase} bg-[#E9EFEA] text-[#718878] hover:bg-[#111A17] hover:text-white`}><MessageSquareText size={22} /></button>
                    <button onClick={() => handleOpenEdit(tenant)} className={`${actionBtnBase} bg-[#F3F8F4] text-[#718878] hover:bg-[#244235] hover:text-white`}><Edit2 size={22} /></button>
                    <button onClick={() => handleDelete(tenant.id)} className={`${actionBtnBase} bg-rose-50 text-rose-300 hover:bg-rose-600 hover:text-white`}><Trash2 size={22} /></button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Modal Unificado */}
      {isModalOpen && (
        <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 transition-all duration-500 ${isClosing ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className="absolute inset-0 bg-[#111A17]/95 backdrop-blur-xl transition-all" onClick={closeModal}></div>
          <div className={`relative bg-white w-full max-w-6xl rounded-[4rem] shadow-[0_100px_200px_rgba(0,0,0,0.8)] overflow-hidden transition-all duration-500 cubic-bezier(0.4, 0, 0.2, 1) transform ${isClosing ? 'scale-95 translate-y-20 opacity-0' : 'scale-100 translate-y-0 opacity-100 animate-in fade-in zoom-in slide-in-from-bottom-24'}`}>
            <div className="flex min-h-[600px] h-[80vh]">
              {/* Barra Lateral do Modal */}
              <div className={`bg-[#111A17] text-white flex flex-col justify-between relative overflow-hidden border-r border-white/5 transition-all duration-500 ease-in-out ${isSidebarOpen ? 'w-1/3 p-10 opacity-100 translate-x-0' : 'w-0 p-0 opacity-0 -translate-x-full pointer-events-none'}`}>
                <button onClick={() => setIsSidebarOpen(false)} className="absolute top-8 right-8 z-30 p-2 text-[#718878] hover:text-white transition-colors"><PanelLeftClose size={24} /></button>
                <div className="absolute -bottom-16 -left-12 opacity-[0.06] rotate-12 pointer-events-none select-none text-[340px] font-black italic">A</div>
                <div className="relative z-10 pt-4 h-full flex flex-col overflow-hidden">
                  <h3 className="text-3xl font-bold tracking-tight uppercase italic text-white flex items-center gap-3">
                    {modalMode === 'report' ? <Briefcase size={28} className="text-[#244235]" /> : null}
                    {modalMode === 'report' ? 'PAINEL' : modalMode === 'edit' ? 'EDITAR' : 'CADASTRO'}
                  </h3>
                  {modalMode === 'report' ? (
                    <div className="flex-1 flex flex-col overflow-hidden mt-6">
                       <div className="flex items-center justify-between border-b border-white/10 pb-2 mb-4">
                          <p className="text-[#718878] text-[10px] font-black uppercase tracking-[0.3em] italic">Diretrizes de Negócio</p>
                          <button onClick={handleAddRule} className="text-[#244235] hover:text-white p-1"><PlusCircle size={18} /></button>
                       </div>
                       <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-4 no-scrollbar">
                         {formData.businessRules.map((rule, idx) => (
                           <div key={idx} className="relative group animate-in fade-in slide-in-from-left-2">
                             <div className="flex items-start gap-3">
                               <div className="mt-3 h-1.5 w-1.5 rounded-full bg-[#244235] flex-shrink-0" />
                               <textarea value={rule} onChange={(e) => handleUpdateRule(idx, e.target.value)} className="w-full bg-transparent text-xs font-medium text-slate-400 leading-relaxed italic border-none focus:ring-0 focus:text-white p-0 resize-none overflow-hidden min-h-[40px]" rows={2} />
                               <button onClick={() => handleRemoveRule(idx)} className="opacity-0 group-hover:opacity-100 text-rose-500/50 hover:text-rose-500 p-1"><Trash size={14} /></button>
                             </div>
                           </div>
                         ))}
                       </div>
                       <section className="mt-8 space-y-4">
                         <p className="text-[#718878] text-[10px] font-black uppercase tracking-[0.3em] italic border-b border-white/10 pb-2">Recursos do Projeto</p>
                         <div className="space-y-2">
                            <a href="#" className="flex items-center gap-3 p-2.5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all">
                               <div className="p-2 rounded-lg bg-[#244235]/20 text-[#244235]"><BookOpen size={14} /></div>
                               <span className="text-[10px] font-bold">Documentação</span>
                            </a>
                            <a href="https://github.com/LucasDpaulo/API_BUSCA_LUCAS.git" target="_blank" className="flex items-center gap-3 p-2.5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all">
                               <div className="p-2 rounded-lg bg-slate-700/20 text-slate-400"><GitBranch size={14} /></div>
                               <span className="text-[10px] font-bold">Repositório Git</span>
                            </a>
                         </div>
                       </section>
                    </div>
                  ) : (
                    <p className="text-[#718878] text-base font-medium leading-relaxed opacity-90 mt-6">Gerencie os parâmetros de conexão e monitore a integridade do pipeline de dados.</p>
                  )}
                </div>
                <div className="relative z-10 text-[10px] font-black text-[#718878] bg-[#718878]/10 px-5 py-2.5 rounded-2xl inline-block tracking-[0.5em] uppercase border border-[#718878]/20 italic shadow-inner text-center mt-4">PLATAFORMA DE GESTÃO</div>
              </div>

              {/* Área de Conteúdo do Modal */}
              <div className="bg-white flex flex-col h-full relative flex-1">
                <button onClick={() => setIsSidebarOpen(true)} className={`absolute top-4 left-4 z-40 p-3 bg-[#F3F8F4] text-[#244235] rounded-xl shadow-lg active:scale-90 transition-all duration-300 ${!isSidebarOpen ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-4 pointer-events-none'}`}><PanelLeftOpen size={24} /></button>
                <div className={`p-10 lg:p-14 overflow-y-auto custom-scrollbar flex-1 bg-gradient-to-br from-white to-slate-50/50 transition-all duration-500 ${!isSidebarOpen ? 'pt-24' : ''}`}>
                  {modalMode !== 'report' ? (
                    <form className="space-y-14" onSubmit={handleSave}>
                      <div className="space-y-10">
                        <div className="flex items-center gap-6"><span className={`text-xs font-black tracking-[0.4em] uppercase text-[#718878] transition-all duration-500 ${!isSidebarOpen ? 'pl-10' : ''}`}>01 . Dados Gerais</span><div className="h-[2px] w-full bg-[#F3F8F4]" /></div>
                        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-end">
                          <div className="md:col-span-4"><label className="block text-[10px] font-black text-[#718878] uppercase mb-4 ml-6 tracking-[0.3em] opacity-80">Nome do Cliente *</label><input type="text" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} placeholder="Ex: Locadora ABC" className={getInputStyle(formData.name)} /></div>
                          <div className="flex flex-col items-center gap-3"><label className="text-[10px] font-black text-[#718878] uppercase tracking-[0.2em] opacity-80 text-center">Ativo</label><div onClick={() => setFormData({...formData, isActive: !formData.isActive})} className={`w-14 h-14 rounded-2xl flex items-center justify-center cursor-pointer transition-all duration-500 border-2 ${formData.isActive ? 'bg-[#244235] border-[#244235] text-white shadow-xl' : 'bg-white border-[#718878]/20 text-[#718878]'}`}><CheckCircle2 size={28} /></div></div>
                        </div>
                      </div>

                      <div className="space-y-10">
                        <div className="flex items-center gap-6"><span className={`text-xs font-black tracking-[0.4em] uppercase text-[#718878] transition-all duration-500 ${!isSidebarOpen ? 'pl-10' : ''}`}>02 . Conectividade Técnica</span><div className="h-[2px] w-full bg-[#F3F8F4]" /></div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-12">
                          <div className="space-y-8">
                            <h4 className="text-xs font-black text-[#244235] uppercase tracking-[0.4em] bg-[#F3F8F4] px-4 py-2 rounded-xl inline-block shadow-sm">API Hinova (SGA)</h4>
                            <input type="text" value={formData.apiToken} onChange={(e) => setFormData({...formData, apiToken: e.target.value})} placeholder="Token gerado no SGA" className={getInputStyle(formData.apiToken)} />
                            <div className="grid grid-cols-2 gap-4">
                              <input type="text" placeholder="Usuário" value={formData.sgaUser} onChange={(e) => setFormData({...formData, sgaUser: e.target.value})} className={getInputStyle(formData.sgaUser)} />
                              <input type="password" placeholder="Senha" value={formData.sgaPass} onChange={(e) => setFormData({...formData, sgaPass: e.target.value})} className={getInputStyle(formData.sgaPass)} />
                            </div>
                          </div>
                          <div className="space-y-8">
                            <h4 className="text-xs font-black text-[#244235] uppercase tracking-[0.4em] bg-[#F3F8F4] px-4 py-2 rounded-xl inline-block shadow-sm">WhatsApp (Destino)</h4>
                            <input type="text" placeholder="Ex: 5531999999999" value={formData.whatsapp} onChange={(e) => setFormData({...formData, whatsapp: e.target.value})} className={getInputStyle(formData.whatsapp)} />
                          </div>
                        </div>
                      </div>
                    </form>
                  ) : (
                    /* MONITORAMENTO */
                    <div className="space-y-10 h-full flex flex-col">
                       <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 px-1">
                        <div className="flex items-center gap-6 flex-1">
                          <span className={`text-xs font-black tracking-[0.4em] uppercase text-[#718878] whitespace-nowrap italic transition-all duration-500 ${!isSidebarOpen ? 'pl-10' : ''}`}>{reportTab === 'message' ? 'Teste de Mensagem' : reportTab === 'logs' ? 'Console de Sistema' : 'Histórico de Testes'}</span>
                          <div className="h-[2px] w-full bg-[#F3F8F4]" />
                        </div>
                        <div className="flex bg-[#F3F8F4] p-1.5 rounded-2xl border border-[#244235]/5 shadow-inner self-start z-10">
                          <button onClick={() => setReportTab('message')} className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${reportTab === 'message' ? 'bg-[#244235] text-white shadow-lg scale-105' : 'text-[#718878] hover:text-[#244235] scale-100'}`}><FlaskConical size={14} /> Teste</button>
                          <button onClick={() => setReportTab('logs')} className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${reportTab === 'logs' ? 'bg-[#111A17] text-white shadow-lg scale-105' : 'text-[#718878] hover:text-[#111A17] scale-100'}`}><Terminal size={14} /> Logs</button>
                          <button onClick={() => { setReportTab('history'); fetchHistory(formData.id); }} className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${reportTab === 'history' ? 'bg-[#244235] text-white shadow-lg scale-105' : 'text-[#718878] hover:text-[#244235] scale-100'}`}><History size={14} /> Histórico</button>
                        </div>
                      </div>

                      {reportTab !== 'history' ? (
                        <div key={reportTab} className="animate-tab-fade-in">
                          <div className={`rounded-[3rem] p-8 lg:p-10 relative overflow-hidden shadow-2xl border-l-[12px] flex-shrink-0 transition-all duration-500 min-h-[300px] ${reportTab === 'logs' ? 'bg-[#111A17] border-[#244235]' : 'bg-[#F3F8F4] border-[#111A17]'}`}>
                            <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">{reportTab === 'logs' ? <Code size={140} className="text-white" /> : <MessageSquare size={140} className="text-[#111A17]" />}</div>
                            <div className="relative z-10 flex justify-between items-start mb-6">
                               <div className={`px-4 py-1.5 rounded-xl border inline-flex items-center gap-2 ${reportTab === 'logs' ? 'bg-[#244235]/20 border-[#244235]/40 text-white' : 'bg-[#111A17]/10 border-[#111A17]/20 text-[#111A17]'}`}>
                                  <div className={`h-1.5 w-1.5 rounded-full animate-pulse ${reportTab === 'logs' ? 'bg-emerald-500' : 'bg-[#111A17]'}`} />
                                  <span className="text-[9px] font-black uppercase tracking-widest">{reportTab === 'logs' ? 'Pipeline Ativo' : 'Preview da Mensagem'}</span>
                               </div>
                               <div className="flex items-center gap-2">
                                 {reportTab === 'logs' && <button onClick={clearLogs} className="text-[#718878] hover:text-rose-500 p-2 transition-colors" title="Limpar logs"><Trash2 size={16} /></button>}
                                 <button onClick={handleCopyReport} className="text-[#718878] hover:text-[#111A17] p-2 transition-colors" title="Copiar"><Copy size={16} /></button>
                               </div>
                            </div>
                            <pre className={`relative z-10 text-base whitespace-pre-wrap opacity-95 ${reportTab === 'logs' ? 'text-[#F3F8F4] font-mono text-sm' : 'text-[#111A17] font-sans font-medium italic'}`}>{reportTab === 'logs' ? formData.technicalLog : formData.lastReport}</pre>
                          </div>

                          <div className="flex flex-col items-start gap-6 w-full mt-4">
                             {reportTab === 'message' && (
                                <div className="flex flex-wrap items-center gap-4">
                                   {!isTesting ? (
                                     <>
                                       <button onClick={handleTest} className="flex items-center gap-3 px-8 py-4 rounded-[2rem] font-black uppercase text-xs tracking-[0.2em] transition-all duration-300 shadow-xl active:scale-95 bg-[#244235] text-white hover:bg-[#111A17]">
                                         <FlaskConical size={18} />
                                         <span>Testar / Verificação de Dados</span>
                                       </button>
                                       <button onClick={handleSendRequest} className="flex items-center gap-3 px-8 py-4 rounded-[2rem] font-black uppercase text-xs tracking-[0.2em] transition-all duration-300 shadow-xl active:scale-95 bg-[#111A17] text-white hover:bg-[#244235]">
                                         <SendHorizontal size={18} />
                                         <span>Disparar para WhatsApp</span>
                                       </button>
                                     </>
                                   ) : (
                                     <>
                                       <div className="flex items-center gap-3 px-8 py-4 rounded-[2rem] bg-amber-50 border-2 border-amber-200 text-amber-700 font-black uppercase text-xs tracking-[0.2em]">
                                         <Loader2 size={18} className="animate-spin" />
                                         <span>{operationType === 'test' ? 'Testando...' : 'Enviando...'}</span>
                                         <span className="font-mono text-sm">{formatTime(elapsedTime)}</span>
                                       </div>
                                       <button onClick={handleCancel} className="flex items-center gap-3 px-8 py-4 rounded-[2rem] font-black uppercase text-xs tracking-[0.2em] transition-all duration-300 shadow-xl active:scale-95 bg-rose-600 text-white hover:bg-rose-700">
                                         <X size={18} />
                                         <span>Parar</span>
                                       </button>
                                     </>
                                   )}
                                </div>
                             )}
                          </div>
                        </div>
                      ) : (
                        /* ABA HISTÓRICO */
                        <div key="history" className="flex-1 overflow-y-auto custom-scrollbar animate-tab-fade-in">
                          {historyLoading ? (
                            <div className="flex items-center justify-center py-20">
                              <Loader2 size={28} className="animate-spin text-[#244235]" />
                              <span className="ml-3 text-sm font-bold text-[#718878]">Carregando histórico...</span>
                            </div>
                          ) : testHistory.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-20 text-center">
                              <History size={48} className="text-[#718878]/30 mb-4" />
                              <p className="text-[#718878] font-bold text-sm">Nenhum teste realizado ainda.</p>
                              <p className="text-[#718878]/60 text-xs mt-1">Execute um teste para ver o histórico aqui.</p>
                            </div>
                          ) : historyFullView !== null ? (
                            /* VISÃO EXPANDIDA — logs fullscreen */
                            <div className="flex flex-col h-full animate-tab-fade-in">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                  <button
                                    onClick={() => setHistoryFullView(null)}
                                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest text-[#718878] hover:text-[#244235] hover:bg-[#F3F8F4] transition-all duration-300"
                                  >
                                    <ArrowRight size={14} className="rotate-180" /> Voltar
                                  </button>
                                  <span className="text-xs font-black text-[#111A17] uppercase tracking-wide">
                                    Teste #{testHistory.length - historyFullView}
                                  </span>
                                  <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${testHistory[historyFullView]?.sucesso ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-rose-50 text-rose-600 border border-rose-100'}`}>
                                    {testHistory[historyFullView]?.sucesso ? 'Sucesso' : 'Falha'}
                                  </span>
                                </div>
                                <span className="text-[10px] text-[#718878] font-medium">
                                  {testHistory[historyFullView] && new Date(testHistory[historyFullView].criado_em).toLocaleString('pt-BR')}
                                </span>
                              </div>
                              <div className="rounded-[2rem] bg-[#111A17] flex-1 overflow-hidden flex flex-col">
                                <div className="flex items-center justify-between px-8 py-4 border-b border-white/5">
                                  <div className="flex items-center gap-2">
                                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-[9px] font-black uppercase tracking-widest text-[#718878]">Logs do Pipeline</span>
                                  </div>
                                  <button
                                    onClick={() => { navigator.clipboard.writeText(testHistory[historyFullView]?.logs || ''); }}
                                    className="text-[#718878] hover:text-white p-2 transition-colors"
                                    title="Copiar logs"
                                  >
                                    <Copy size={14} />
                                  </button>
                                </div>
                                <pre className="flex-1 p-8 text-sm text-[#F3F8F4] font-mono whitespace-pre-wrap overflow-y-auto custom-scrollbar opacity-90 leading-relaxed">
                                  {testHistory[historyFullView]?.logs || 'Nenhum log disponível.'}
                                </pre>
                              </div>
                            </div>
                          ) : (
                            /* LISTA DE HISTÓRICO */
                            <div className="space-y-4">
                            {testHistory.map((item, idx) => (
                              <div key={item.id} className="rounded-[2rem] border border-[#718878]/10 overflow-hidden transition-all duration-300 hover:shadow-lg">
                                <button
                                  onClick={() => { setExpandedHistory(expandedHistory === idx ? null : idx); setHistoryDetailTab('message'); }}
                                  className="w-full flex items-center justify-between px-8 py-5 bg-white hover:bg-[#F3F8F4]/50 transition-colors"
                                >
                                  <div className="flex items-center gap-4">
                                    <div className={`h-3 w-3 rounded-full flex-shrink-0 ${item.sucesso ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                                    <div className="text-left">
                                      <span className="text-xs font-black text-[#111A17] uppercase tracking-wide">
                                        Teste #{testHistory.length - idx}
                                      </span>
                                      <p className="text-[10px] text-[#718878] font-medium mt-0.5">
                                        {new Date(item.criado_em).toLocaleString('pt-BR')}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-3">
                                    <span className={`px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest ${item.sucesso ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-rose-50 text-rose-600 border border-rose-100'}`}>
                                      {item.sucesso ? 'Sucesso' : 'Falha'}
                                    </span>
                                    {expandedHistory === idx ? <ChevronUp size={16} className="text-[#718878]" /> : <ChevronDown size={16} className="text-[#718878]" />}
                                  </div>
                                </button>
                                {expandedHistory === idx && (
                                  <div className="border-t border-[#718878]/10 animate-tab-fade-in">
                                    {/* Sub-abas: Mensagem / Logs */}
                                    <div className="flex items-center gap-1 px-6 pt-4 pb-2">
                                      <button
                                        onClick={() => setHistoryDetailTab('message')}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${historyDetailTab === 'message' ? 'bg-[#244235] text-white shadow-lg scale-105' : 'text-[#718878] hover:text-[#244235] scale-100'}`}
                                      >
                                        <MessageSquareText size={12} /> Mensagem
                                      </button>
                                      {item.logs && (
                                        <button
                                          onClick={() => setHistoryDetailTab('logs')}
                                          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest transition-all duration-300 ${historyDetailTab === 'logs' ? 'bg-[#111A17] text-white shadow-lg scale-105' : 'text-[#718878] hover:text-[#111A17] scale-100'}`}
                                        >
                                          <Terminal size={12} /> Logs
                                        </button>
                                      )}
                                    </div>

                                    {/* Conteúdo da sub-aba */}
                                    <div key={historyDetailTab} className="animate-tab-fade-in">
                                      {historyDetailTab === 'message' ? (
                                        <div className="p-6 bg-[#F3F8F4]/30">
                                          <pre className="text-sm text-[#111A17] font-sans font-medium italic whitespace-pre-wrap bg-white rounded-2xl p-5 border border-[#718878]/10 max-h-[250px] overflow-y-auto custom-scrollbar">
                                            {item.mensagem}
                                          </pre>
                                        </div>
                                      ) : (
                                        <div className="p-6 bg-[#111A17] relative">
                                          <div className="flex items-center justify-between mb-3">
                                            <p className="text-[10px] font-black text-[#718878] uppercase tracking-[0.3em]">Logs do pipeline</p>
                                            <button
                                              onClick={() => setHistoryFullView(idx)}
                                              className="flex items-center gap-1.5 text-[9px] font-black uppercase tracking-widest text-[#718878] hover:text-white transition-colors"
                                            >
                                              <Eye size={12} /> Expandir
                                            </button>
                                          </div>
                                          <pre className="text-xs text-[#F3F8F4] font-mono whitespace-pre-wrap max-h-[180px] overflow-y-auto custom-scrollbar opacity-80">
                                            {item.logs}
                                          </pre>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                {modalMode !== 'report' && (
                  <div className="p-8 border-t border-[#F3F8F4] bg-white flex justify-end gap-8">
                    <button onClick={closeModal} className="text-[#718878] font-black uppercase text-[10px] tracking-[0.4em] hover:text-rose-600">Fechar</button>
                    <button onClick={handleSave} className="bg-[#111A17] text-white px-10 py-4 rounded-[2.2rem] font-black uppercase text-xs tracking-[0.2em] shadow-2xl active:scale-95">Entendido</button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmação de Disparo */}
      {confirmDisparo && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-[#111A17]/15 backdrop-blur-[2px]" onClick={() => setConfirmDisparo(false)} />
          <div className="relative bg-white rounded-[3rem] p-10 max-w-md w-full shadow-[0_40px_80px_rgba(0,0,0,0.4)] text-center animate-in fade-in zoom-in duration-300">
            <h3 className="text-xl font-black text-[#111A17] uppercase tracking-wide mb-3">Confirmar Disparo</h3>
            <p className="text-[#718878] text-sm font-medium leading-relaxed mb-2">
              A mensagem do preview será enviada agora para o número de WhatsApp cadastrado.
            </p>
            <p className="text-[#718878] text-xs mb-8">
              Esta ação expira automaticamente em <span className="font-black text-[#244235]">{confirmCountdown}s</span>
            </p>
            <div className="w-full bg-[#F3F8F4] rounded-full h-1.5 mb-8 overflow-hidden">
              <div
                className="bg-[#244235] h-full rounded-full transition-all duration-1000 ease-linear"
                style={{ width: `${(confirmCountdown / 10) * 100}%` }}
              />
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setConfirmDisparo(false)}
                className="flex-1 py-4 rounded-[2rem] font-black uppercase text-[10px] tracking-[0.3em] text-[#718878] border-2 border-[#718878]/10 hover:border-rose-300 hover:text-rose-600 transition-all"
              >
                Cancelar
              </button>
              <button
                onClick={handleSendConfirm}
                className="flex-1 py-4 rounded-[2rem] font-black uppercase text-[10px] tracking-[0.3em] bg-[#244235] text-white shadow-xl hover:bg-[#111A17] transition-all active:scale-95"
              >
                Sim, Enviar
              </button>
            </div>
          </div>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #71887830; border-radius: 10px; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        @keyframes fade-in-sidebar { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
        .animate-fade-in-sidebar { animation: fade-in-sidebar 0.6s ease-out forwards; }
        .animate-in { animation: fade-in-simple 0.5s ease-out, zoom-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1); }
        @keyframes fade-in-simple { from { opacity: 0; } to { opacity: 1; } }
        @keyframes zoom-in { from { transform: scale(0.92); } to { transform: scale(1); } }
        @keyframes tab-fade-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .animate-tab-fade-in { animation: tab-fade-in 0.4s ease-out forwards; }
      `}} />
    </div>
  );
};

export default App;