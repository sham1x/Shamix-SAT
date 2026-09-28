/* Shamix Prep SAT — Complete Vanilla JS Full-Stack Application Logic */

// ==========================================
// 1. STATE STORE & SECURITY HELPERS
// ==========================================
const appState = {
  user: null,
  currentView: "dashboard",
  homeworkFilter: "all",
  leaderboardPeriod: "week",
  attendanceMonth: null, // YYYY-MM
  activeLesson: null,
  activeHomework: null,
  activeHomeworkDetail: null,
  quizCurrentIndex: 0,
  quizUserAnswers: {}, // { questionId: selectedIndex }
  quizQuestionResults: {}, // { questionId: { is_correct, correct_index, explanation } }
  lessonProgressTimer: null
};

// Global 401 Unauthorized handler triggered by api.js
window.onUnauthorized = function() {
  appState.user = null;
  renderAuthView();
};

// Security helper: Escape HTML to prevent XSS attacks
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Initials Avatar generator (Deterministic colors derived from username)
function getUserAvatarHtml(nameOrUsername, sizeClass = "w-9 h-9 text-xs") {
  const name = nameOrUsername || "User";
  const words = name.trim().split(/\s+/);
  let initials = "";
  if (words.length >= 2) {
    initials = (words[0][0] + words[1][0]).toUpperCase();
  } else if (words[0] && words[0].length >= 2) {
    initials = words[0].slice(0, 2).toUpperCase();
  } else {
    initials = (words[0] ? words[0][0] : "U").toUpperCase();
  }

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const gradients = [
    "from-purple-500 to-indigo-600",
    "from-cyan-500 to-blue-600",
    "from-emerald-500 to-teal-600",
    "from-amber-500 to-orange-600",
    "from-rose-500 to-pink-600",
    "from-violet-500 to-purple-600",
    "from-fuchsia-500 to-pink-600"
  ];
  const selectedGrad = gradients[Math.abs(hash) % gradients.length];

  return `
    <div class="${sizeClass} rounded-full bg-gradient-to-br ${selectedGrad} flex items-center justify-center text-white font-bold tracking-wider shadow-sm shrink-0 border border-white/20">
      ${escapeHtml(initials)}
    </div>
  `;
}

// Monogram SVG helper
function getShamixMonogramSvg(sizeClass = "w-8 h-8") {
  return `
    <svg class="${sizeClass} rounded-xl shrink-0" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="shamix-logo-grad-inline" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8B5CF6" />
          <stop offset="100%" stop-color="#06B6D4" />
        </linearGradient>
      </defs>
      <rect width="100" height="100" rx="24" fill="url(#shamix-logo-grad-inline)" />
      <path d="M 62 34 C 62 26, 38 24, 38 36 C 38 48, 62 48, 62 62 C 62 76, 36 74, 36 66" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round" />
      <path d="M 68 22 L 73 14 L 78 22 L 86 27 L 78 32 L 73 40 L 68 32 L 60 27 Z" fill="#FDE047" />
    </svg>
  `;
}

// UI State renderers: Loading Skeleton, Empty State, Error State
function renderSkeletonList(count = 3) {
  let skeletons = "";
  for (let i = 0; i < count; i++) {
    skeletons += `
      <div class="glass-panel p-5 rounded-2xl border border-slate-800 animate-pulse space-y-3">
        <div class="flex justify-between items-center">
          <div class="h-4 bg-slate-800 rounded w-1/3"></div>
          <div class="h-4 bg-slate-800 rounded w-1/6"></div>
        </div>
        <div class="h-3 bg-slate-800/60 rounded w-2/3"></div>
        <div class="h-8 bg-slate-800 rounded w-full mt-2"></div>
      </div>
    `;
  }
  return `<div class="space-y-4">${skeletons}</div>`;
}

function renderEmptyState(message, actionLabel = null, actionFnStr = null) {
  return `
    <div class="glass-panel p-8 sm:p-12 rounded-2xl border border-slate-800/80 text-center space-y-3 my-4">
      <div class="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mx-auto text-xl">
        <i class="fa-solid fa-folder-open"></i>
      </div>
      <h3 class="font-bold text-base text-slate-200">${escapeHtml(message)}</h3>
      <p class="text-xs text-slate-400 max-w-md mx-auto">No records found for this view right now.</p>
      ${actionLabel && actionFnStr ? `
        <button onclick="${actionFnStr}" class="mt-2 bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-4 rounded-xl text-xs shadow-md shadow-purple-600/30 transition-all">
          ${escapeHtml(actionLabel)}
        </button>
      ` : ""}
    </div>
  `;
}

function renderErrorState(errorMessage, retryFnStr) {
  return `
    <div class="glass-panel p-6 sm:p-8 rounded-2xl border border-rose-500/30 bg-rose-950/10 text-center space-y-3 my-4">
      <div class="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto text-xl">
        <i class="fa-solid fa-triangle-exclamation"></i>
      </div>
      <h3 class="font-bold text-base text-rose-200">Failed to load data</h3>
      <p class="text-xs text-rose-300/80 max-w-md mx-auto">${escapeHtml(errorMessage)}</p>
      <button onclick="${retryFnStr}" class="mt-2 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 px-4 rounded-xl text-xs shadow-md shadow-rose-600/30 transition-all flex items-center gap-2 mx-auto">
        <i class="fa-solid fa-rotate-right"></i>
        <span>Retry</span>
      </button>
    </div>
  `;
}

// ==========================================
// 2. AUTHENTICATION CONTROLLER & VIEWS
// ==========================================
function switchAuthTab(tab) {
  const loginForm = document.getElementById("form-login");
  const regForm = document.getElementById("form-register");
  const loginTab = document.getElementById("auth-tab-login");
  const regTab = document.getElementById("auth-tab-register");

  if (tab === "login") {
    loginForm.classList.remove("hidden");
    regForm.classList.add("hidden");
    loginTab.className = "flex-1 py-2 rounded-lg text-xs font-bold transition-all bg-purple-600 text-white shadow-md";
    regTab.className = "flex-1 py-2 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white";
  } else {
    loginForm.classList.add("hidden");
    regForm.classList.remove("hidden");
    regTab.className = "flex-1 py-2 rounded-lg text-xs font-bold transition-all bg-purple-600 text-white shadow-md";
    loginTab.className = "flex-1 py-2 rounded-lg text-xs font-bold transition-all text-slate-400 hover:text-white";
  }
}

function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);
  if (input.type === "password") {
    input.type = "text";
    icon.className = "fa-solid fa-eye-slash text-xs";
  } else {
    input.type = "password";
    icon.className = "fa-solid fa-eye text-xs";
  }
}

function fillDemoAccount() {
  switchAuthTab("login");
  document.getElementById("login-username").value = "demo";
  document.getElementById("login-password").value = "Demo12345!";
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const usernameInput = document.getElementById("login-username");
  const passwordInput = document.getElementById("login-password");
  const submitBtn = document.getElementById("login-submit-btn");
  const errContainer = document.getElementById("login-error-container");
  const errText = document.getElementById("login-error-text");

  errContainer.classList.add("hidden");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch animate-spin"></i> <span>Signing in...</span>`;

  try {
    const res = await ShamixApi.login(usernameInput.value.trim(), passwordInput.value);
    appState.user = res.user;
    showAppView();
    navigateTo("dashboard");
  } catch (err) {
    errText.textContent = err.message || "Invalid username or password";
    errContainer.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>Sign In</span> <i class="fa-solid fa-arrow-right text-xs"></i>`;
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("reg-username").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const display_name = document.getElementById("reg-displayname").value.trim() || username;
  const password = document.getElementById("reg-password").value;
  const submitBtn = document.getElementById("reg-submit-btn");
  const errContainer = document.getElementById("reg-error-container");
  const errText = document.getElementById("reg-error-text");

  if (username.length < 3) {
    errText.textContent = "Username must be at least 3 characters long.";
    errContainer.classList.remove("hidden");
    return;
  }
  if (password.length < 8) {
    errText.textContent = "Password must be at least 8 characters long.";
    errContainer.classList.remove("hidden");
    return;
  }

  errContainer.classList.add("hidden");
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch animate-spin"></i> <span>Creating account...</span>`;

  try {
    const res = await ShamixApi.register(username, email, password, display_name);
    appState.user = res.user;
    showAppView();
    navigateTo("dashboard");
  } catch (err) {
    errText.textContent = err.message || "Registration failed. Username or email may be taken.";
    errContainer.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>Create Account & Start Learning</span> <i class="fa-solid fa-user-plus text-xs"></i>`;
  }
}

function handleLogout() {
  ShamixApi.clearToken();
  appState.user = null;
  renderAuthView();
}

function renderAuthView() {
  document.getElementById("view-auth").classList.remove("hidden");
  document.getElementById("app-container").classList.add("hidden");
  const userDropdown = document.getElementById("user-dropdown-menu");
  if (userDropdown) userDropdown.classList.add("hidden");
}

function showAppView() {
  document.getElementById("view-auth").classList.add("hidden");
  document.getElementById("app-container").classList.remove("hidden");
  updateHeaderUserStats();
}

function toggleUserDropdown() {
  const menu = document.getElementById("user-dropdown-menu");
  if (menu) menu.classList.toggle("hidden");
}

// Update header stats & user information
function updateHeaderUserStats() {
  if (!appState.user) return;
  const u = appState.user;

  // Streak, XP, Level
  const streakEl = document.getElementById("streak-count");
  const xpEl = document.getElementById("xp-count");
  const lvlEl = document.getElementById("user-level");

  if (streakEl) streakEl.textContent = u.streak_current || 0;
  if (xpEl) xpEl.textContent = (u.xp || 0).toLocaleString();
  if (lvlEl) lvlEl.textContent = u.level || 1;

  // User Avatar & Name in Header
  const avatarContainer = document.getElementById("header-avatar-container");
  const usernameEl = document.getElementById("header-username");
  const dropdownName = document.getElementById("dropdown-user-name");
  const dropdownEmail = document.getElementById("dropdown-user-email");

  if (avatarContainer) {
    avatarContainer.innerHTML = getUserAvatarHtml(u.display_name || u.username, "w-7 h-7 text-xs");
  }
  if (usernameEl) usernameEl.textContent = escapeHtml(u.display_name || u.username);
  if (dropdownName) dropdownName.textContent = escapeHtml(u.display_name || u.username);
  if (dropdownEmail) dropdownEmail.textContent = escapeHtml(u.email || "");

  // Update Countdown timer
  updateCountdownDisplay(u.target_test_date);
}

// Countdown Calculation Timer
function updateCountdownDisplay(targetDateIso) {
  const timerEl = document.getElementById("header-countdown-timer");
  if (!timerEl) return;

  if (!targetDateIso) {
    timerEl.textContent = "60 Days Remaining";
    return;
  }

  const target = new Date(targetDateIso).getTime();
  const now = new Date().getTime();
  const diff = target - now;

  if (diff <= 0) {
    timerEl.textContent = "🎉 SAT Test Day!";
    return;
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  timerEl.textContent = `${days}d ${hours}h ${mins}m`;
}

// ==========================================
// 3. NAVIGATION & ROUTER CONTROLLER
// ==========================================
function navigateTo(viewName) {
  appState.currentView = viewName;

  // Highlight active sidebar navigation buttons
  document.querySelectorAll(".nav-item, .mobile-nav-item").forEach(btn => {
    btn.classList.remove("text-purple-400", "bg-purple-500/10", "border", "border-purple-500/20");
    btn.classList.add("text-slate-400");
  });

  const activeDesktopBtn = document.getElementById(`nav-${viewName}`);
  const activeMobileBtn = document.getElementById(`mobile-nav-${viewName}`);

  if (activeDesktopBtn) {
    activeDesktopBtn.classList.remove("text-slate-400");
    activeDesktopBtn.classList.add("text-purple-400", "bg-purple-500/10", "border", "border-purple-500/20");
  }
  if (activeMobileBtn) {
    activeMobileBtn.classList.remove("text-slate-400");
    activeMobileBtn.classList.add("text-purple-400");
  }

  // Close Coach chat drawer if navigating on mobile
  const drawer = document.getElementById("coach-chat-drawer");
  if (drawer && window.innerWidth < 640) {
    drawer.classList.add("translate-x-full");
  }

  // Render view content
  switch (viewName) {
    case "dashboard":
      renderDashboardView();
      break;
    case "lessons":
      renderLessonsView();
      break;
    case "homework":
      renderHomeworkView();
      break;
    case "leaderboard":
      renderLeaderboardView();
      break;
    case "attendance":
      renderAttendanceView();
      break;
    case "flashcards":
      renderFlashcardsView();
      break;
    case "badges":
      renderBadgesView();
      break;
    default:
      renderDashboardView();
  }
}

// ==========================================
// 4. SCREEN VIEWS IMPLEMENTATION
// ==========================================

// --- VIEW 1: DASHBOARD ---
async function renderDashboardView() {
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(3);

  try {
    const data = await ShamixApi.getDashboard();
    appState.user = data.user;
    updateHeaderUserStats();

    const u = data.user;
    const todayLesson = data.todayLesson;
    const pendingHomework = data.pendingHomework || [];

    main.innerHTML = `
      <div class="space-y-6">
        
        <!-- DASHBOARD HERO BANNER -->
        <div class="glass-panel-glow rounded-3xl p-6 sm:p-8 border border-purple-500/30 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div class="space-y-2 max-w-xl z-10">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full">
                Digital SAT Target: 1550+
              </span>
              <span class="text-xs text-amber-400 font-semibold flex items-center gap-1">
                <i class="fa-solid fa-fire"></i> ${u.streak_current} Day Streak
              </span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-white font-heading tracking-tight">
              Welcome back, <span class="bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">${escapeHtml(u.display_name)}</span>!
            </h2>
            <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">
              You are on track! Complete today's recommended masterclass and daily homework to level up your score.
            </p>
          </div>

          <!-- Hero Quick Stats Card -->
          <div class="grid grid-cols-2 gap-3 w-full md:w-auto z-10">
            <div class="bg-slate-900/90 border border-slate-800 p-3.5 rounded-2xl text-center">
              <div class="text-[10px] uppercase font-bold text-slate-400">Total XP</div>
              <div class="text-xl font-extrabold text-cyan-400 font-mono">${u.xp.toLocaleString()}</div>
            </div>
            <div class="bg-slate-900/90 border border-slate-800 p-3.5 rounded-2xl text-center">
              <div class="text-[10px] uppercase font-bold text-slate-400">Leaderboard Rank</div>
              <div class="text-xl font-extrabold text-amber-400 font-mono">#${data.leaderboardRank}</div>
            </div>
          </div>
        </div>

        <!-- RECOMMENDED TODAY'S LESSON & PENDING DRILLS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- Today's Lesson (2 Cols) -->
          <div class="lg:col-span-2 space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="font-bold text-base text-slate-100 font-heading flex items-center gap-2">
                <i class="fa-solid fa-play-circle text-purple-400"></i> Today's Recommended Masterclass
              </h3>
              <button onclick="navigateTo('lessons')" class="text-xs text-purple-400 hover:text-purple-300 font-semibold">View All Lessons &rarr;</button>
            </div>

            ${todayLesson ? `
              <div class="glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div class="space-y-2 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 text-[10px] font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">${escapeHtml(todayLesson.subject)}</span>
                    <span class="text-xs text-slate-400"><i class="fa-regular fa-clock mr-1"></i>${escapeHtml(todayLesson.duration)}</span>
                  </div>
                  <h4 class="font-bold text-base text-white hover:text-purple-300 cursor-pointer" onclick="openLessonModal('${todayLesson.id}')">${escapeHtml(todayLesson.title)}</h4>
                  <p class="text-xs text-slate-400 line-clamp-2">${escapeHtml(todayLesson.description)}</p>
                </div>
                <button onclick="openLessonModal('${todayLesson.id}')" class="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold py-2.5 px-5 rounded-xl text-xs flex items-center justify-center gap-2 shadow-md shadow-purple-600/30 shrink-0">
                  <i class="fa-solid fa-play"></i> Watch Lesson
                </button>
              </div>
            ` : renderEmptyState("No lesson assigned for today.")}

            <!-- PENDING HOMEWORK DRILLS -->
            <div class="space-y-3 pt-2">
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-base text-slate-100 font-heading flex items-center gap-2">
                  <i class="fa-solid fa-clipboard-check text-cyan-400"></i> Pending Homework Drills
                </h3>
                <button onclick="navigateTo('homework')" class="text-xs text-cyan-400 hover:text-cyan-300 font-semibold">Homework Hub &rarr;</button>
              </div>

              ${pendingHomework.length > 0 ? pendingHomework.map(hw => `
                <div class="glass-panel p-4 rounded-2xl border border-slate-800 flex items-center justify-between gap-3">
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-cyan-400 uppercase tracking-wider">${escapeHtml(hw.subject)}</span>
                      <span class="text-[10px] text-amber-400 font-semibold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">+${hw.xpReward} XP</span>
                    </div>
                    <h4 class="font-bold text-xs sm:text-sm text-slate-100">${escapeHtml(hw.title)}</h4>
                  </div>
                  <button onclick="startQuiz('${hw.id}')" class="bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2 px-3.5 rounded-xl text-xs shadow-md shadow-cyan-600/20 shrink-0">
                    Start Drill
                  </button>
                </div>
              `).join("") : renderEmptyState("All homework drills completed! 🎉")}
            </div>
          </div>

          <!-- DASHBOARD RIGHT SIDEBAR (Stats & Check-in) -->
          <div class="space-y-4">
            
            <!-- ATTENDANCE & CHECKIN CARD -->
            <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="font-bold text-sm text-slate-100 font-heading">Daily Attendance</h4>
                <span class="text-xs font-bold text-emerald-400">${data.attendanceRate}% Rate</span>
              </div>
              <p class="text-xs text-slate-400">Check in daily to build your study streak and earn +50 Stardust XP!</p>
              <button onclick="checkInToday()" class="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/20 transition-all">
                <i class="fa-solid fa-calendar-check"></i> Daily Check-In (+50 XP)
              </button>
            </div>

            <!-- TARGET TEST DATE CARD -->
            <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="font-bold text-sm text-slate-100 font-heading">Target Test Date</h4>
                <button onclick="openCountdownModal()" class="text-xs text-purple-400 hover:text-purple-300 font-semibold">Change</button>
              </div>
              <div class="text-xs text-slate-300 font-mono font-bold bg-slate-900 p-3 rounded-xl border border-slate-800 text-center">
                ${new Date(u.target_test_date || Date.now()).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>

          </div>

        </div>

      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderDashboardView()");
  }
}

// --- VIEW 2: VIDEO LESSONS ---
async function renderLessonsView() {
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(4);

  try {
    const lessons = await ShamixApi.getLessons();

    if (!lessons || lessons.length === 0) {
      main.innerHTML = renderEmptyState("No video lessons available at the moment.");
      return;
    }

    main.innerHTML = `
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-extrabold text-white font-heading">Digital SAT Video Masterclasses</h2>
            <p class="text-xs text-slate-400">Master core concepts with step-by-step video tutorials</p>
          </div>
        </div>

        <!-- Lessons Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          ${lessons.map(les => `
            <div class="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition-all flex flex-col justify-between space-y-4">
              <div class="space-y-2">
                <div class="flex items-center justify-between text-xs">
                  <span class="px-2 py-0.5 font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">${escapeHtml(les.subject)}</span>
                  <span class="text-slate-400 font-medium"><i class="fa-regular fa-clock mr-1"></i>${escapeHtml(les.duration)}</span>
                </div>
                <h3 class="font-bold text-base text-white hover:text-purple-300 cursor-pointer" onclick="openLessonModal('${les.id}')">${escapeHtml(les.title)}</h3>
                <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">${escapeHtml(les.description)}</p>
              </div>

              <div class="space-y-3 pt-2">
                <!-- Progress Bar -->
                <div class="space-y-1">
                  <div class="flex justify-between text-[10px] text-slate-400 font-semibold">
                    <span>Progress</span>
                    <span>${les.progress}%</span>
                  </div>
                  <div class="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                    <div class="bg-gradient-to-r from-purple-500 to-cyan-400 h-1.5 rounded-full" style="width: ${les.progress}%"></div>
                  </div>
                </div>

                <button onclick="openLessonModal('${les.id}')" class="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-md shadow-purple-600/30 transition-all">
                  <i class="fa-solid fa-play"></i> Watch Masterclass
                </button>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderLessonsView()");
  }
}

async function openLessonModal(lessonId) {
  const modal = document.getElementById("lesson-modal");
  const modalTitle = document.getElementById("lesson-modal-title");
  const modalSubject = document.getElementById("lesson-modal-subject");
  const modalModule = document.getElementById("lesson-modal-module");
  const modalContent = document.getElementById("lesson-modal-content");

  modalContent.innerHTML = renderSkeletonList(2);
  modal.classList.remove("hidden");
  modal.classList.add("flex");

  try {
    const les = await ShamixApi.getLesson(lessonId);
    appState.activeLesson = les;

    modalTitle.textContent = les.title;
    modalSubject.textContent = les.subject.toUpperCase();
    modalModule.textContent = les.module || les.subject;

    const takeawaysHtml = (les.keyTakeaways || []).map(t => `<li class="flex items-start gap-2"><i class="fa-solid fa-check text-cyan-400 mt-1"></i> <span>${escapeHtml(t)}</span></li>`).join("");
    const transcriptHtml = (les.transcript || []).map(tr => `
      <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-3 text-xs">
        <span class="font-mono text-cyan-400 shrink-0 font-bold">${tr.time}s</span>
        <span class="text-slate-300">${escapeHtml(tr.text)}</span>
      </div>
    `).join("");

    modalContent.innerHTML = `
      <div class="space-y-6">
        <!-- Video Player -->
        <div class="aspect-video bg-black rounded-2xl overflow-hidden border border-slate-800 relative">
          <video id="lesson-video-player" controls class="w-full h-full object-cover">
            <source src="${escapeHtml(les.videoUrl)}" type="video/mp4">
            Your browser does not support HTML5 video.
          </video>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed">${escapeHtml(les.description)}</p>

        <!-- Key Takeaways -->
        <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800 space-y-2">
          <h4 class="font-bold text-xs uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
            <i class="fa-solid fa-key"></i> Key SAT Takeaways
          </h4>
          <ul class="space-y-1.5 text-xs text-slate-200">
            ${takeawaysHtml}
          </ul>
        </div>

        <!-- Transcript -->
        <div class="space-y-2">
          <h4 class="font-bold text-xs uppercase tracking-wider text-slate-400">Lesson Transcript</h4>
          <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
            ${transcriptHtml}
          </div>
        </div>

        <!-- Go to Related Homework Link -->
        ${les.relatedHomeworkId ? `
          <div class="pt-2">
            <button onclick="closeLessonModal(); startQuiz('${les.relatedHomeworkId}')" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-3 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/30">
              <i class="fa-solid fa-pencil"></i> Go to Practice Homework Drill
            </button>
          </div>
        ` : ""}
      </div>
    `;

    // Setup video progress tracking
    const videoEl = document.getElementById("lesson-video-player");
    if (videoEl) {
      videoEl.ontimeupdate = () => {
        if (appState.lessonProgressTimer) clearTimeout(appState.lessonProgressTimer);
        appState.lessonProgressTimer = setTimeout(() => {
          const currentSec = Math.floor(videoEl.currentTime);
          const isCompleted = videoEl.ended || (videoEl.duration > 0 && currentSec >= videoEl.duration - 5);
          ShamixApi.updateLessonProgress(les.id, currentSec, isCompleted).catch(() => {});
        }, 1000);
      };
    }

  } catch (err) {
    modalContent.innerHTML = renderErrorState(err.message, `openLessonModal('${lessonId}')`);
  }
}

function closeLessonModal() {
  const modal = document.getElementById("lesson-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
  const videoEl = document.getElementById("lesson-video-player");
  if (videoEl) videoEl.pause();
}

// --- VIEW 3: HOMEWORK HUB ---
async function renderHomeworkView(statusFilter = appState.homeworkFilter) {
  appState.homeworkFilter = statusFilter;
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(4);

  try {
    const list = await ShamixApi.getHomework(statusFilter);

    const tabs = [
      { id: "all", label: "All Drills" },
      { id: "not_started", label: "Not Started" },
      { id: "in_progress", label: "In Progress" },
      { id: "completed", label: "Completed" }
    ];

    const tabsHtml = tabs.map(t => `
      <button onclick="renderHomeworkView('${t.id}')" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${appState.homeworkFilter === t.id ? 'bg-purple-600 text-white shadow-md' : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'}">
        ${t.label}
      </button>
    `).join("");

    main.innerHTML = `
      <div class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-2xl font-extrabold text-white font-heading">Homework & Practice Drills</h2>
            <p class="text-xs text-slate-400">Server-graded SAT practice questions with step-by-step solutions</p>
          </div>
          <!-- Filter Tabs -->
          <div class="flex items-center gap-1.5 overflow-x-auto whitespace-nowrap">
            ${tabsHtml}
          </div>
        </div>

        <!-- Homework Grid -->
        ${list.length > 0 ? `
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            ${list.map(hw => {
              let statusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-slate-800 text-slate-400 border border-slate-700">Not Started</span>`;
              if (hw.status === "completed") {
                statusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Completed (${escapeHtml(hw.score)})</span>`;
              } else if (hw.status === "in_progress") {
                statusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">In Progress</span>`;
              } else if (hw.status === "overdue") {
                statusBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">Overdue</span>`;
              }

              return `
                <div class="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col justify-between space-y-4">
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider">${escapeHtml(hw.subject)} • ${escapeHtml(hw.skill)}</span>
                      ${statusBadge}
                    </div>
                    <h3 class="font-bold text-base text-white">${escapeHtml(hw.title)}</h3>
                    <div class="flex items-center gap-4 text-xs text-slate-400">
                      <span><i class="fa-regular fa-question-circle mr-1"></i>${hw.questionCount} Questions</span>
                      <span><i class="fa-regular fa-clock mr-1"></i>${escapeHtml(hw.estTime)}</span>
                      <span class="text-amber-400 font-bold"><i class="fa-solid fa-gem mr-1"></i>+${hw.xpReward} XP</span>
                    </div>
                  </div>

                  <button onclick="startQuiz('${hw.id}')" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2 shadow-md shadow-cyan-600/20 transition-all">
                    <i class="fa-solid fa-pencil"></i> ${hw.status === 'completed' ? 'Review & Practice Again' : 'Start Practice Drill'}
                  </button>
                </div>
              `;
            }).join("")}
          </div>
        ` : renderEmptyState("No homework drills found for this filter.")}
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderHomeworkView()");
  }
}

// --- QUIZ FLOW CONTROLLER ---
async function startQuiz(homeworkId) {
  const modal = document.getElementById("quiz-modal");
  const modalSubject = document.getElementById("quiz-subject-badge");
  const modalTitle = document.getElementById("quiz-title");

  try {
    await ShamixApi.startHomework(homeworkId);
    const hwDetail = await ShamixApi.getHomeworkDetail(homeworkId);

    appState.activeHomeworkDetail = hwDetail;
    appState.quizCurrentIndex = 0;
    appState.quizUserAnswers = {};
    appState.quizQuestionResults = {};

    modalSubject.textContent = hwDetail.subject.toUpperCase();
    modalTitle.textContent = hwDetail.title;

    modal.classList.remove("hidden");
    modal.classList.add("flex");

    renderCurrentQuizQuestion();
  } catch (err) {
    alert(`Could not start quiz: ${err.message}`);
  }
}

function renderCurrentQuizQuestion() {
  const hw = appState.activeHomeworkDetail;
  if (!hw || !hw.questions || hw.questions.length === 0) return;

  const idx = appState.quizCurrentIndex;
  const q = hw.questions[idx];

  document.getElementById("quiz-current-num").textContent = idx + 1;
  document.getElementById("quiz-total-num").textContent = hw.questions.length;
  document.getElementById("quiz-topic").textContent = `Topic: ${q.topic || hw.skill}`;
  document.getElementById("quiz-difficulty").textContent = `Difficulty: ${q.difficulty || 'Medium'}`;
  document.getElementById("quiz-question-text").textContent = q.stem;

  const container = document.getElementById("quiz-options-container");
  const explanationBox = document.getElementById("quiz-explanation-box");
  const explanationText = document.getElementById("quiz-explanation-text");

  const selectedIdx = appState.quizUserAnswers[q.id];
  const serverResult = appState.quizQuestionResults[q.id];

  let optionsHtml = "";
  (q.options || []).forEach((optText, oIdx) => {
    let optionStyle = "border-slate-800 hover:border-purple-500/50 bg-slate-900/60 text-slate-200";

    if (serverResult) {
      if (oIdx === serverResult.correct_index) {
        optionStyle = "border-emerald-500 bg-emerald-950/40 text-emerald-200 font-bold";
      } else if (selectedIdx === oIdx && !serverResult.is_correct) {
        optionStyle = "border-rose-500 bg-rose-950/40 text-rose-200";
      }
    } else if (selectedIdx === oIdx) {
      optionStyle = "border-purple-500 bg-purple-950/40 text-purple-200 font-bold";
    }

    optionsHtml += `
      <button onclick="selectQuizOption(${q.id}, ${oIdx})" ${serverResult ? 'disabled' : ''} class="w-full text-left p-3.5 rounded-xl border transition-all text-xs flex items-center gap-3 ${optionStyle}">
        <span class="w-6 h-6 rounded-lg bg-slate-800 flex items-center justify-center font-mono font-bold text-[11px] shrink-0">${String.fromCharCode(65 + oIdx)}</span>
        <span class="flex-1">${escapeHtml(optText)}</span>
      </button>
    `;
  });

  container.innerHTML = optionsHtml;

  if (serverResult) {
    explanationText.textContent = serverResult.explanation;
    explanationBox.classList.remove("hidden");
  } else {
    explanationBox.classList.add("hidden");
  }

  // Prev / Action Button controls
  const prevBtn = document.getElementById("quiz-prev-btn");
  const actionBtn = document.getElementById("quiz-action-btn");

  prevBtn.disabled = (idx === 0);

  if (serverResult) {
    if (idx < hw.questions.length - 1) {
      actionBtn.textContent = "Next Question →";
      actionBtn.className = "px-6 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/30";
    } else {
      actionBtn.textContent = "Submit Homework Drill";
      actionBtn.className = "px-6 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30";
    }
  } else {
    actionBtn.textContent = "Submit Answer";
    actionBtn.className = "px-6 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold shadow-lg shadow-purple-600/30";
  }
}

function selectQuizOption(questionId, optionIndex) {
  if (appState.quizQuestionResults[questionId]) return; // already answered
  appState.quizUserAnswers[questionId] = optionIndex;
  renderCurrentQuizQuestion();
}

function prevQuizQuestion() {
  if (appState.quizCurrentIndex > 0) {
    appState.quizCurrentIndex--;
    renderCurrentQuizQuestion();
  }
}

async function handleQuizAction() {
  const hw = appState.activeHomeworkDetail;
  const idx = appState.quizCurrentIndex;
  const q = hw.questions[idx];

  const selectedIdx = appState.quizUserAnswers[q.id];
  const serverResult = appState.quizQuestionResults[q.id];

  // If question is not answered yet -> send answer to server
  if (!serverResult) {
    if (selectedIdx === undefined) {
      alert("Please select an option before submitting!");
      return;
    }

    try {
      const res = await ShamixApi.submitAnswer(hw.id, q.id, selectedIdx);
      appState.quizQuestionResults[q.id] = {
        is_correct: res.is_correct,
        correct_index: res.correct_index,
        explanation: res.explanation
      };
      renderCurrentQuizQuestion();
    } catch (err) {
      alert(`Could not submit answer: ${err.message}`);
    }
    return;
  }

  // If question is already answered and we're not on last question -> Next question
  if (idx < hw.questions.length - 1) {
    appState.quizCurrentIndex++;
    renderCurrentQuizQuestion();
    return;
  }

  // If on last question -> Submit full homework drill
  try {
    const finalRes = await ShamixApi.submitHomework(hw.id);
    closeQuizModal();

    // Trigger celebratory canvas confetti if 100% or XP rewarded
    if (typeof confetti === "function") {
      confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
    }

    let msg = `🎉 Drill Completed!\n\nScore: ${finalRes.score}\nXP Earned: +${finalRes.xp_rewarded} XP`;
    if (finalRes.newly_unlocked_badges && finalRes.newly_unlocked_badges.length > 0) {
      msg += `\n\n🏆 Unlocked Badges: ${finalRes.newly_unlocked_badges.join(", ")}`;
    }
    alert(msg);

    // Refresh user & views
    const me = await ShamixApi.getMe();
    appState.user = me;
    updateHeaderUserStats();
    if (appState.currentView === "homework") renderHomeworkView();

  } catch (err) {
    alert(`Could not submit homework: ${err.message}`);
  }
}

function closeQuizModal() {
  const modal = document.getElementById("quiz-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  }
}

// --- VIEW 4: LEADERBOARD ---
async function renderLeaderboardView(period = appState.leaderboardPeriod) {
  appState.leaderboardPeriod = period;
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(4);

  try {
    const data = await ShamixApi.getLeaderboard(period);
    const standings = data.standings || [];
    const userRank = data.userRank;

    main.innerHTML = `
      <div class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-2xl font-extrabold text-white font-heading">SAT Stardust Leaderboard</h2>
            <p class="text-xs text-slate-400">Compete with top students across the nation</p>
          </div>
          <!-- Period Switcher -->
          <div class="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
            <button onclick="renderLeaderboardView('week')" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${period === 'week' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}">This Week</button>
            <button onclick="renderLeaderboardView('all_time')" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${period === 'all_time' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'}">All Time</button>
          </div>
        </div>

        <!-- Standings Table -->
        <div class="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
          <div class="divide-y divide-slate-800/80">
            ${standings.map(s => {
              let rankBadge = `<span class="font-mono font-bold text-xs text-slate-400">#${s.rank}</span>`;
              if (s.rank === 1) rankBadge = `<span class="text-amber-400 font-extrabold text-sm flex items-center gap-1"><i class="fa-solid fa-crown text-amber-400"></i> #1</span>`;
              else if (s.rank === 2) rankBadge = `<span class="text-slate-300 font-bold text-sm flex items-center gap-1"><i class="fa-solid fa-medal text-slate-300"></i> #2</span>`;
              else if (s.rank === 3) rankBadge = `<span class="text-amber-600 font-bold text-sm flex items-center gap-1"><i class="fa-solid fa-medal text-amber-600"></i> #3</span>`;

              return `
                <div class="p-4 flex items-center justify-between gap-4 transition-all ${s.isUser ? 'bg-purple-950/40 border-l-4 border-purple-500' : 'hover:bg-slate-900/40'}">
                  <div class="flex items-center gap-4">
                    <div class="w-10 shrink-0 text-center">${rankBadge}</div>
                    ${getUserAvatarHtml(s.name, "w-9 h-9 text-xs")}
                    <div>
                      <div class="font-bold text-sm text-slate-100 flex items-center gap-2">
                        <span>${escapeHtml(s.name)}</span>
                        ${s.isUser ? `<span class="text-[9px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30">YOU</span>` : ""}
                      </div>
                      <div class="text-[11px] text-slate-400 flex items-center gap-2">
                        <span><i class="fa-solid fa-fire text-amber-400 mr-1"></i>${s.streak}d Streak</span>
                      </div>
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="font-extrabold text-sm text-cyan-400 font-mono">${s.xp.toLocaleString()} XP</div>
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        </div>

        <!-- Sticky User Rank Summary -->
        ${userRank ? `
          <div class="glass-panel-glow p-4 rounded-2xl border border-purple-500/30 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="font-extrabold text-amber-400 text-sm">Your Standing: #${userRank.rank}</span>
              <span class="text-xs text-slate-300">| ${userRank.xp.toLocaleString()} XP</span>
            </div>
            <span class="text-xs text-purple-400 font-semibold">Keep grinding to reach top #3!</span>
          </div>
        ` : ""}
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderLeaderboardView()");
  }
}

// --- VIEW 5: ATTENDANCE & CHECK-IN ---
async function renderAttendanceView(monthStr = appState.attendanceMonth) {
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(3);

  try {
    const data = await ShamixApi.getAttendance(monthStr);
    const daysAttended = data.daysAttended || [];
    const daysMissed = data.daysMissed || [];
    const upcoming = data.upcomingLiveSessions || [];

    const now = new Date();
    const curYear = now.getFullYear();
    const curMonth = now.getMonth() + 1;
    const daysInMonth = new Date(curYear, curMonth, 0).getDate();

    main.innerHTML = `
      <div class="space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 class="text-2xl font-extrabold text-white font-heading">Attendance & Daily Check-in</h2>
            <p class="text-xs text-slate-400">Maintain attendance consistency for +50 Stardust XP per day</p>
          </div>
          <button onclick="checkInToday()" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold py-2.5 px-5 rounded-xl text-xs flex items-center gap-2 shadow-md shadow-emerald-600/20">
            <i class="fa-solid fa-calendar-check"></i> Daily Check-In (+50 XP)
          </button>
        </div>

        <!-- Attendance Stats & Calendar Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- Calendar (2 Cols) -->
          <div class="lg:col-span-2 glass-panel p-5 sm:p-6 rounded-2xl border border-slate-800 space-y-4">
            <div class="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 class="font-bold text-sm text-slate-100 font-heading">September 2026 Activity Grid</h3>
              <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">${data.attendanceRate}% Attendance Rate</span>
            </div>

            <!-- Days Grid -->
            <div class="grid grid-cols-7 gap-2 text-center text-xs">
              ${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d => `<div class="font-bold text-slate-500 py-1">${d}</div>`).join("")}

              ${Array.from({ length: daysInMonth }, (_, i) => i + 1).map(day => {
                let cellStyle = "bg-slate-900/60 border-slate-800 text-slate-400";
                let icon = "";
                if (daysAttended.includes(day)) {
                  cellStyle = "bg-emerald-950/50 border-emerald-500/40 text-emerald-300 font-bold";
                  icon = `<i class="fa-solid fa-check text-[10px] block text-emerald-400 mt-0.5"></i>`;
                } else if (daysMissed.includes(day)) {
                  cellStyle = "bg-rose-950/40 border-rose-500/30 text-rose-400";
                  icon = `<i class="fa-solid fa-xmark text-[10px] block text-rose-400 mt-0.5"></i>`;
                }

                return `
                  <div class="p-2.5 rounded-xl border ${cellStyle} h-12 flex flex-col items-center justify-center">
                    <span>${day}</span>
                    ${icon}
                  </div>
                `;
              }).join("")}
            </div>
          </div>

          <!-- Upcoming Live Sessions -->
          <div class="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <h3 class="font-bold text-sm text-slate-100 font-heading flex items-center gap-2">
              <i class="fa-solid fa-video text-purple-400"></i> Upcoming SAT Masterclasses
            </h3>

            ${upcoming.length > 0 ? upcoming.map(s => `
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <div class="text-[10px] font-bold text-purple-400 uppercase tracking-wider">${escapeHtml(s.time)}</div>
                <h4 class="font-bold text-xs text-white">${escapeHtml(s.title)}</h4>
                <p class="text-[11px] text-slate-400">Instructor: ${escapeHtml(s.instructor)}</p>
              </div>
            `).join("") : renderEmptyState("No live masterclasses scheduled.")}
          </div>

        </div>
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderAttendanceView()");
  }
}

async function checkInToday() {
  try {
    const res = await ShamixApi.checkIn();
    alert(res.message);
    const me = await ShamixApi.getMe();
    appState.user = me;
    updateHeaderUserStats();
    if (appState.currentView === "attendance") renderAttendanceView();
  } catch (err) {
    alert(`Check-in failed: ${err.message}`);
  }
}

// --- VIEW 6: FLASHCARDS ---
async function renderFlashcardsView() {
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(3);

  try {
    const cards = await ShamixApi.getFlashcards();

    if (!cards || cards.length === 0) {
      main.innerHTML = renderEmptyState("No flashcards available.");
      return;
    }

    main.innerHTML = `
      <div class="space-y-6">
        <div>
          <h2 class="text-2xl font-extrabold text-white font-heading">SAT Formulas & Vocabulary Flashcards</h2>
          <p class="text-xs text-slate-400">Interactive flip cards for quick memory revision</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          ${cards.map((c, i) => `
            <div class="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 cursor-pointer group hover:border-purple-500/40 transition-all" onclick="toggleFlashcard('fc-card-${i}')">
              <div class="flex items-center justify-between text-xs">
                <span class="px-2.5 py-0.5 font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">${escapeHtml(c.category)}</span>
                <span class="text-slate-500 text-[11px]">Click to Flip 🔄</span>
              </div>

              <div id="fc-card-${i}" class="space-y-3 min-h-[120px] flex flex-col justify-center">
                <div class="front-side font-bold text-base text-white text-center">${escapeHtml(c.front)}</div>
                <div class="back-side hidden text-xs text-cyan-300 bg-slate-900 p-4 rounded-xl border border-slate-800 whitespace-pre-line leading-relaxed">${escapeHtml(c.back)}</div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderFlashcardsView()");
  }
}

function toggleFlashcard(cardId) {
  const container = document.getElementById(cardId);
  if (!container) return;
  const front = container.querySelector(".front-side");
  const back = container.querySelector(".back-side");
  if (front && back) {
    front.classList.toggle("hidden");
    back.classList.toggle("hidden");
  }
}

// --- VIEW 7: BADGES ---
async function renderBadgesView() {
  const main = document.getElementById("main-content");
  main.innerHTML = renderSkeletonList(3);

  try {
    const badges = await ShamixApi.getBadges();

    main.innerHTML = `
      <div class="space-y-6">
        <div>
          <h2 class="text-2xl font-extrabold text-white font-heading">Achievement Badges</h2>
          <p class="text-xs text-slate-400">Unlock prestigious badges by achieving study milestones</p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          ${badges.map(b => `
            <div class="glass-panel p-5 rounded-2xl border ${b.unlocked ? 'border-amber-500/40 bg-amber-950/10' : 'border-slate-800 opacity-60'} flex items-center gap-4">
              <div class="w-14 h-14 rounded-2xl ${b.unlocked ? 'bg-gradient-to-br from-amber-500/20 to-purple-500/20 border border-amber-500/40 text-amber-400' : 'bg-slate-900 border border-slate-800 text-slate-600'} flex items-center justify-center text-2xl shrink-0 shadow-lg">
                <i class="${escapeHtml(b.icon)}"></i>
              </div>
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <h4 class="font-bold text-sm text-white">${escapeHtml(b.title)}</h4>
                  ${b.unlocked ? `<span class="text-[9px] font-bold bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/30">UNLOCKED</span>` : `<span class="text-[9px] font-bold bg-slate-800 text-slate-500 px-2 py-0.5 rounded-full">LOCKED</span>`}
                </div>
                <p class="text-xs text-slate-400 line-clamp-2">${escapeHtml(b.desc)}</p>
                <div class="text-[10px] font-mono text-purple-400">${escapeHtml(b.progress)}</div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  } catch (err) {
    main.innerHTML = renderErrorState(err.message, "renderBadgesView()");
  }
}

// --- MODALS & DRAWER HELPERS ---
function toggleCoachChat() {
  const drawer = document.getElementById("coach-chat-drawer");
  if (drawer) drawer.classList.toggle("translate-x-full");
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById("coach-input");
  if (input) {
    input.value = promptText;
    handleCoachSubmit(new Event("submit"));
  }
}

function handleCoachSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("coach-input");
  const container = document.getElementById("coach-chat-messages");
  if (!input || !input.value.trim()) return;

  const text = input.value.trim();
  input.value = "";

  // Append user message
  container.innerHTML += `
    <div class="flex gap-2.5 items-start justify-end">
      <div class="bg-purple-600 text-white p-3 rounded-2xl rounded-tr-none max-w-[85%] leading-relaxed text-xs">
        ${escapeHtml(text)}
      </div>
    </div>
  `;

  // Simulated AI Coach response
  setTimeout(() => {
    let reply = `Great question! When studying for the SAT, keep in mind that practice and strategy are key. ${escapeHtml(text)} is covered in detail in our masterclasses.`;
    if (text.toLowerCase().includes("quadratic")) {
      reply = "For Quadratic equations, remember x = (-b ± √(b² - 4ac)) / (2a). If the discriminant b² - 4ac = 0, there is exactly 1 real solution!";
    } else if (text.toLowerCase().includes("reading")) {
      reply = "On Digital SAT Reading, always eliminate choices with extreme words ('always', 'never'). Look for pivot transition words like 'however' or 'consequently'.";
    }

    container.innerHTML += `
      <div class="flex gap-2.5 items-start">
        ${getShamixMonogramSvg("w-7 h-7 rounded-lg shrink-0")}
        <div class="bg-slate-800/90 text-slate-200 p-3 rounded-2xl rounded-tl-none border border-slate-700/60 max-w-[85%] leading-relaxed text-xs">
          ${reply}
        </div>
      </div>
    `;
    container.scrollTop = container.scrollHeight;
  }, 600);

  container.scrollTop = container.scrollHeight;
}

function toggleGraphingCalc() {
  const modal = document.getElementById("graphing-calc-modal");
  if (modal) modal.classList.toggle("hidden");
}

function openCountdownModal() {
  const modal = document.getElementById("countdown-modal");
  const input = document.getElementById("target-date-input");
  if (input && appState.user && appState.user.target_test_date) {
    input.value = appState.user.target_test_date.slice(0, 16);
  }
  if (modal) modal.classList.remove("hidden");
}

function closeCountdownModal() {
  const modal = document.getElementById("countdown-modal");
  if (modal) modal.classList.add("hidden");
}

async function saveCustomCountdown() {
  const input = document.getElementById("target-date-input");
  if (!input || !input.value) return;

  try {
    const updated = await ShamixApi.updateMe({ target_test_date: input.value });
    appState.user = updated;
    updateHeaderUserStats();
    closeCountdownModal();
    alert("🎉 Target SAT Test Date updated!");
  } catch (err) {
    alert(`Failed to update date: ${err.message}`);
  }
}

// ==========================================
// 5. APPLICATION INITIALIZATION
// ==========================================
document.addEventListener("DOMContentLoaded", async () => {
  const token = ShamixApi.getToken();
  if (!token) {
    renderAuthView();
    return;
  }

  try {
    const user = await ShamixApi.getMe();
    appState.user = user;
    showAppView();
    navigateTo("dashboard");
  } catch (err) {
    renderAuthView();
  }
});
