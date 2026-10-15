const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const loginMessage = document.getElementById('login-message');
const welcomeUser = document.getElementById('welcome-user');
const userRole = document.getElementById('user-role');
const userForm = document.getElementById('user-form');
const userMessage = document.getElementById('user-message');

const whatsappInputGroup = document.getElementById('whatsapp-input-group');
const whatsappNumInput = document.getElementById('whatsapp-num');
const codigoInputGroup = document.getElementById('codigo-input-group');
const codigoWhatsappInput = document.getElementById('codigo-whatsapp');

const state = {
  usuario: null,
  alunos: [],
  usuarios: [],
  logs: [],
};

const telaMap = {
  overview: 'overview',
  students: 'students',
  users: 'users',
  logs: 'logs',
};

const API_BASE = '';

function setMessage(element, text, type = '') {
  element.textContent = text;
  element.className = `message ${type}`.trim();
}

function showScreen(screenName) {
  loginScreen.classList.toggle('active', screenName === 'login');
  dashboardScreen.classList.toggle('active', screenName === 'dashboard');

  document.querySelectorAll('.panel').forEach((panel) => {
    panel.classList.toggle('active', panel.id === 'overview' && screenName === 'dashboard');
  });

  const panels = ['overview', 'students', 'users', 'logs'];
  panels.forEach((id) => {
    const panel = document.getElementById(id);
    panel.classList.toggle('active', id === 'overview');
  });
}

async function fetchJson(url, options = {}) {
  const requestUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
  const response = await fetch(requestUrl, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const text = await response.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch (error) {
      throw new Error('Resposta inválida da API.');
    }
  }

  if (!response.ok) {
    throw new Error((data && data.message) || 'Erro na requisição');
  }

  return data;
}

async function loadData() {
  try {
    const [alunos, usuarios, logs, relatorio] = await Promise.all([
      fetchJson('/api/alunos'),
      fetchJson('/api/usuarios'),
      fetchJson('/api/logs'),
      fetchJson('/api/relatorio')
    ]);

    state.alunos = alunos;
    state.usuarios = usuarios;
    state.logs = logs;
    renderDashboard(relatorio);
    renderUsers();
    renderLogs();
    renderAlunos();
  } catch (error) {
    console.error(error);
  }
}

function renderDashboard(relatorio) {
  document.getElementById('total-alunos').textContent = relatorio.total ?? 0;
  document.getElementById('aprovados').textContent = relatorio.aprovados ?? 0;
  document.getElementById('recuperacao').textContent = relatorio.recuperacao ?? 0;
  document.getElementById('reprovados').textContent = relatorio.reprovados ?? 0;
  document.getElementById('media-turma').textContent = Number(relatorio.media_turma || 0).toFixed(1);
  document.getElementById('melhor-aluno').textContent = relatorio.melhor_aluno ? `${relatorio.melhor_aluno.nome} (${relatorio.melhor_aluno.media.toFixed(1)})` : 'Nenhum';
  document.getElementById('pior-aluno').textContent = relatorio.pior_aluno ? `${relatorio.pior_aluno.nome} (${relatorio.pior_aluno.media.toFixed(1)})` : 'Nenhum';
}

function renderAlunos() {
  const tbody = document.getElementById('alunos-table');
  tbody.innerHTML = '';

  state.alunos.forEach((aluno) => {
    const [, nome, n1, n2, n3] = aluno;
    const media = ((Number(n1) + Number(n2) + Number(n3)) / 3).toFixed(1);
    const status = Number(media) >= 7 ? 'Aprovado' : Number(media) >= 4 ? 'Recuperação' : 'Reprovado';

    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${aluno[0]}</td>
      <td>${nome}</td>
      <td>${Number(n1).toFixed(1)}</td>
      <td>${Number(n2).toFixed(1)}</td>
      <td>${Number(n3).toFixed(1)}</td>
      <td>${media}</td>
      <td>${status}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderUsers() {
  const tbody = document.getElementById('usuarios-table');
  tbody.innerHTML = '';

  state.usuarios.forEach((usuario) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${usuario.usuario}</td>
      <td>${usuario.tipo}</td>
    `;
    tbody.appendChild(row);
  });
}

function renderLogs() {
  const tbody = document.getElementById('logs-table');
  tbody.innerHTML = '';

  state.logs.forEach((log) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${log.usuario}</td>
      <td>${log.tipo}</td>
      <td>${log.status}</td>
      <td>${log.data_hora}</td>
    `;
    tbody.appendChild(row);
  });
}

async function login(event) {
  event.preventDefault();
  const usuario = document.getElementById('usuario').value.trim();
  const senha = document.getElementById('senha').value.trim();
  const whatsapp = whatsappNumInput.value.trim();
  const codigo = codigoWhatsappInput.value.trim();

  try {
    const response = await fetch(`${API_BASE}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usuario, senha, whatsapp, codigo }),
    });

    const result = await response.json();

    // Validação correta baseada no campo 'ok' retornado pela API
    if (!result.ok) {
      if (result.precisa_whatsapp) {
        whatsappInputGroup.style.display = 'flex';
        whatsappNumInput.required = true;
        setMessage(loginMessage, result.message, 'success');
        return;
      }
      if (result.precisa_codigo) {
        whatsappInputGroup.style.display = 'none';
        whatsappNumInput.required = false;
        codigoInputGroup.style.display = 'flex';
        codigoWhatsappInput.required = true;
        setMessage(loginMessage, result.message, 'success');
        return;
      }
      throw new Error(result.message || 'Erro no login');
    }

    state.usuario = result.usuario;
    welcomeUser.textContent = `Bem-vindo, ${result.usuario.usuario}`;
    userRole.textContent = result.usuario.tipo === 'admin' ? 'Administrador' : 'Funcionário';
    setMessage(loginMessage, 'Login realizado com sucesso!', 'success');
    loginForm.reset();
    whatsappInputGroup.style.display = 'none';
    whatsappNumInput.required = false;
    codigoInputGroup.style.display = 'none';
    codigoWhatsappInput.required = false;
    await loadData();
    showScreen('dashboard');
  } catch (error) {
    setMessage(loginMessage, error.message, 'error');
  }
}

async function cadastrarUsuario(event) {
  event.preventDefault();
  const usuario = document.getElementById('new-user').value.trim();
  const senha = document.getElementById('new-password').value.trim();
  const tipo = document.getElementById('new-role').value;

  try {
    await fetchJson('/api/usuarios/add', {
      method: 'POST',
      body: JSON.stringify({ usuario, senha, tipo }),
    });

    setMessage(userMessage, 'Usuário cadastrado com sucesso!', 'success');
    userForm.reset();
    await loadData();
  } catch (error) {
    setMessage(userMessage, error.message, 'error');
  }
}

function bindNavigation() {
  document.querySelectorAll('.nav-btn').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      const target = button.dataset.target;
      document.querySelectorAll('.panel').forEach((panel) => {
        panel.classList.toggle('active', panel.id === telaMap[target]);
      });
    });
  });
}

function logout() {
  state.usuario = null;
  whatsappInputGroup.style.display = 'none';
  whatsappNumInput.required = false;
  whatsappNumInput.value = '';
  codigoInputGroup.style.display = 'none';
  codigoWhatsappInput.required = false;
  codigoWhatsappInput.value = '';
  showScreen('login');
  setMessage(loginMessage, '', '');
}

loginForm.addEventListener('submit', login);
userForm.addEventListener('submit', cadastrarUsuario);
document.getElementById('logout-btn').addEventListener('click', logout);
bindNavigation();
showScreen('login');
loadData();