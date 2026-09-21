import React, { useEffect, useState } from 'react';
import { Eye, EyeSlash, User, Lock, Sparkle } from '@phosphor-icons/react';
import { useNavigate } from 'react-router-dom';
import { login as loginApi } from '../../../services/api/authService';
import { useAuthContext } from '../../../context/AuthContext';

const ROLE_DEFAULT_ROUTE = {
    super_admin: '/super/dashboard',
    tenant_admin: '/admin/dashboard',
    teacher: '/teacher/dashboard',
    TEACHER: '/teacher/dashboard',
    parent: '/parent/dashboard',
};

const Login = () => {
    const navigate = useNavigate();
    const { login: authLogin } = useAuthContext();

    // استخراج النطاق الفرعي من الرابط (مثال: alhuda.manarasy.com -> alhuda)
    const getSubdomain = () => {
        const hostname = window.location.hostname;
        const parts = hostname.split('.');
        if (parts.length >= 2 && parts[0] !== 'www') {
            return parts[0];
        }
        return '';
    };

    const [form, setForm] = useState({ subdomain: getSubdomain(), username: '', password: '' });
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [characterIdle, setCharacterIdle] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setCharacterIdle(true), 1850);
        return () => clearTimeout(timer);
    }, []);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!form.username || !form.password) {
            setError('يرجى تعبئة جميع الحقول');
            return;
        }
        if (!form.subdomain) {
            setError('لم يتم التعرف على النطاق الفرعي من الرابط. يرجى استخدام رابط مثل: alhuda.localhost');
            return;
        }
        setLoading(true);
        setError('');
        try {
            const data = await loginApi(form);
            if (data.status === 'success') {
                const userData = {
                    id: data.data.user.id,
                    username: data.data.user.username,
                    role: data.data.user.role,
                    tenant_id: data.data.tenant.id,
                    tenant_name: data.data.tenant.name,
                };
                // حفظ في localStorage للتوافق مع الكود القديم
                localStorage.setItem('access_token', data.data.access_token);
                localStorage.setItem('tenant_id', data.data.tenant.id);
                localStorage.setItem('tenant_name', data.data.tenant.name);
                localStorage.setItem('user_role', data.data.user.role);
                localStorage.setItem('username', data.data.user.username);
                localStorage.setItem('user', JSON.stringify(userData));
                // تحديث AuthContext
                authLogin(userData, { access: data.data.access_token });
                // التوجيه حسب الدور
                const userRole = data.data.user.role ? data.data.user.role.toLowerCase() : '';
                const route = ROLE_DEFAULT_ROUTE[userRole] || '/admin/dashboard';
                navigate(route, { replace: true });
            } else {
                setError(data.message || 'فشل تسجيل الدخول');
            }
        } catch (err) {
            const msg = err.response?.data?.message || 'حدث خطأ في الاتصال بالخادم';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    if (!form.subdomain) {
        return (
            <div className="landing-page">
                <div className="landing-content">
                    <div className="login-logo-circle landing-logo">
                        <span className="login-logo-icon">✦</span>
                    </div>
                    <h1 className="login-brand-name" style={{ color: 'var(--primary-green)' }}>مَنَارَة</h1>
                    <p className="login-brand-tagline" style={{ color: 'var(--text-secondary)' }}>منصة إدارة الحلقات القرآنية</p>
                    <p className="login-brand-desc" style={{ color: 'var(--text-muted)' }}>
                        نلتقي لنرتقي في رحاب القرآن الكريم — متابعة حفظ، تسميع، وتنظيم متكامل لحلقات الذكر في واجهة عصرية مريحة.
                    </p>
                    <button className="landing-register-btn" onClick={() => navigate('/register')}>
                        طلب تسجيل مسجد جديد
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="login-page">
            {/* Left Panel - Brand */}
            <div className="login-brand-panel">
                <div className="login-brand-pattern"></div>
                <div className="login-brand-content">
                    <div className="login-logo-circle">
                        <span className="login-logo-icon">✦</span>
                    </div>
                    <h1 className="login-brand-name">مَنَارَة</h1>
                    <p className="login-brand-tagline">منصة إدارة الحلقات القرآنية</p>
                    <p className="login-brand-desc">
                        نلتقي لنرتقي في رحاب القرآن الكريم — متابعة حفظ، تسميع، وتنظيم متكامل لحلقات الذكر في واجهة عصرية مريحة.
                    </p>
                </div>

                {/* Animated student character: walks in, sets down their bag, and settles in to study */}
                <div className="login-character-stage" aria-hidden="true">
                    <div className="login-character-shadow"></div>
                    <div
                        className={[
                            'login-character',
                            characterIdle ? 'is-idle' : '',
                            passwordFocused ? 'is-covering-eyes' : '',
                            loading ? 'is-celebrating' : '',
                        ].filter(Boolean).join(' ')}
                    >
                        <div className="login-character-bounce">
                            <svg className="login-character-rig" viewBox="0 0 220 340" width="100%" height="100%">
                                {/* Backpack */}
                                <g className="login-character-backpack">
                                    <rect x="120" y="156" width="44" height="56" rx="12" fill="var(--accent-orange)" />
                                    <rect x="130" y="146" width="24" height="16" rx="6" fill="var(--accent-orange)" />
                                    <rect x="136" y="168" width="12" height="18" rx="3" fill="#00000022" />
                                    <rect x="126" y="176" width="32" height="7" rx="3.5" fill="#ffffff33" />
                                </g>

                                {/* Legs */}
                                <g className="login-character-leg-left" style={{ transformOrigin: '94px 206px' }}>
                                    <rect x="82" y="206" width="24" height="76" rx="11" fill="#2b2b3a" />
                                    <rect x="77" y="278" width="32" height="15" rx="7" fill="#f7f6f1" />
                                </g>
                                <g className="login-character-leg-right" style={{ transformOrigin: '124px 206px' }}>
                                    <rect x="112" y="206" width="24" height="76" rx="11" fill="#2b2b3a" />
                                    <rect x="109" y="278" width="32" height="15" rx="7" fill="#f7f6f1" />
                                </g>

                                {/* Torso */}
                                <g className="login-character-torso">
                                    <rect x="64" y="126" width="90" height="88" rx="28" fill="#f7f6f1" />
                                    <path d="M64 154 q26 14 90 0 v-8 q-45 16 -90 0 z" fill="var(--accent-orange)" />
                                    <rect x="64" y="126" width="90" height="18" rx="9" fill="var(--accent-orange)" />

                                    {/* Book held at chest */}
                                    <g className="login-character-book">
                                        <rect x="118" y="176" width="30" height="22" rx="2" fill="#ffffff" />
                                        <rect x="118" y="176" width="30" height="22" rx="2" fill="none" stroke="var(--primary-green)" strokeWidth="1.5" />
                                        <line x1="133" y1="178" x2="133" y2="196" stroke="var(--primary-green)" strokeWidth="1.5" />
                                        <line x1="122" y1="183" x2="130" y2="183" stroke="#c9c4b8" strokeWidth="1.4" />
                                        <line x1="122" y1="188" x2="130" y2="188" stroke="#c9c4b8" strokeWidth="1.4" />
                                        <line x1="136" y1="183" x2="144" y2="183" stroke="#c9c4b8" strokeWidth="1.4" />
                                        <line x1="136" y1="188" x2="144" y2="188" stroke="#c9c4b8" strokeWidth="1.4" />
                                    </g>

                                    {/* Arms */}
                                    <g className="login-character-arm-left" style={{ transformOrigin: '67px 134px' }}>
                                        <rect x="56" y="134" width="22" height="72" rx="11" fill="#f7f6f1" />
                                        <circle cx="67" cy="204" r="12" fill="#e3a97e" />
                                    </g>
                                    <g className="login-character-arm-right" style={{ transformOrigin: '151px 134px' }}>
                                        <rect x="140" y="134" width="22" height="72" rx="11" fill="#f7f6f1" />
                                        <circle cx="151" cy="204" r="12" fill="#e3a97e" />
                                    </g>

                                    {/* Head */}
                                    <g className="login-character-head" style={{ transformOrigin: '110px 126px' }}>
                                        <circle cx="110" cy="78" r="40" fill="#e3a97e" />
                                        <circle cx="72" cy="80" r="7" fill="#e3a97e" />
                                        <circle cx="148" cy="80" r="7" fill="#e3a97e" />
                                        <path d="M68,72 A46,44 0 0 1 152,72 Q110,64 68,72 Z" fill="#3a2a1e" />
                                        <path d="M68,72 Q64,86 70,98" fill="none" stroke="#3a2a1e" strokeWidth="8" strokeLinecap="round" />
                                        <path d="M152,72 Q156,86 150,98" fill="none" stroke="#3a2a1e" strokeWidth="8" strokeLinecap="round" />
                                        <g className="login-character-brow">
                                            <rect x="90" y="70" width="13" height="4" rx="2" fill="#3a2a1e" />
                                            <rect x="117" y="70" width="13" height="4" rx="2" fill="#3a2a1e" />
                                        </g>
                                        <g className="login-character-eye"><ellipse cx="97" cy="82" rx="4" ry="5" fill="var(--primary-green)" /></g>
                                        <g className="login-character-eye login-character-eye-right"><ellipse cx="123" cy="82" rx="4" ry="5" fill="var(--primary-green)" /></g>
                                        <circle cx="82" cy="94" r="6" fill="var(--accent-orange)" opacity="0.18" />
                                        <circle cx="138" cy="94" r="6" fill="var(--accent-orange)" opacity="0.18" />
                                        <path d="M98 96 q12 10 24 0" stroke="#a05a2c" strokeWidth="3" fill="none" strokeLinecap="round" />

                                        {/* Peeking hands, shown while typing the password */}
                                        <g className="login-character-peek-hands">
                                            <circle cx="95" cy="80" r="13" fill="#e3a97e" />
                                            <circle cx="125" cy="80" r="13" fill="#e3a97e" />
                                        </g>
                                    </g>
                                </g>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Panel - Form */}
            <div className="login-form-panel">
                <div className="login-card">
                    <div className="login-card-header">
                        <h2>مرحباً بعودتك</h2>
                        <p>سجل دخولك لمتابعة لوحة التحكم وإدارة حلقاتك القرآنية</p>
                    </div>

                    <form className="login-form" onSubmit={handleSubmit}>
                        {/* Username */}
                        <div className="login-field">
                            <label htmlFor="username">اسم المستخدم</label>
                            <div className="login-input-wrapper">
                                <User size={20} className="login-input-icon" />
                                <input
                                    id="username"
                                    type="text"
                                    name="username"
                                    value={form.username}
                                    onChange={handleChange}
                                    placeholder="name@example.com"
                                    className="login-input with-icon"
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div className="login-field">
                            <div className="login-field-row">
                                <label htmlFor="password">كلمة المرور</label>
                                <button type="button" className="login-forgot">نسيت كلمة المرور؟</button>
                            </div>
                            <div className="login-input-wrapper">
                                <Lock size={20} className="login-input-icon" />
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    onFocus={() => setPasswordFocused(true)}
                                    onBlur={() => setPasswordFocused(false)}
                                    placeholder="••••••••••••"
                                    className="login-input with-icon"
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    className="login-eye-btn"
                                    onClick={() => setShowPassword(!showPassword)}
                                    aria-label={showPassword ? 'إخفاء كلمة المرور' : 'إظهار كلمة المرور'}
                                >
                                    {showPassword ? <EyeSlash size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
                        </div>

                        {/* Remember Me */}
                        <div className="login-remember">
                            <label className="login-checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                    className="login-checkbox"
                                />
                                <span>تذكرني</span>
                            </label>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="login-error" role="alert">
                                {error}
                            </div>
                        )}

                        {/* Submit */}
                        <button
                            id="login-submit-btn"
                            type="submit"
                            className="login-btn-primary"
                            disabled={loading}
                        >
                            {loading ? <span className="login-spinner"></span> : 'تسجيل الدخول'}
                        </button>

                        <div className="login-divider"><span>أو</span></div>

                        <button type="button" className="login-btn-google">
                            <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            تسجيل الدخول بواسطة جوجل
                        </button>

                        <button type="button" className="login-btn-secondary" onClick={() => navigate('/register')}>طلب تسجيل</button>

                        <p className="login-register-link">
                            ليس لديك حساب؟ <button type="button" className="login-link-btn" onClick={() => navigate('/register')}>سجل الآن</button>
                        </p>
                    </form>

                    <button type="button" className="login-assistant-btn">
                        <Sparkle size={18} weight="fill" />
                        مساعد منارة الذكي
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;


