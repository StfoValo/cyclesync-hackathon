/**
 * CycleSync Icon Library
 * Custom SVG icons not available in Lucide.
 * All functions return raw SVG/HTML strings.
 */

// ─── Powertrain / Engine ────────────────────────────────────────────────────

/** Electric zap bolt */
export const iconElectric = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;

/** Petrol fuel pump */
export const iconPetrol = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22V6a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16"/><path d="M14 9h2a2 2 0 0 1 2 2v2.5a1.5 1.5 0 0 0 3 0V7l-3-3"/><path d="M3 22h11"/><rect x="5" y="9" width="6" height="4" rx="1"/></svg>`;

/** Hybrid leaf + bolt */
export const iconHybrid = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>`;

/** EV Battery (more refined than lucide battery) */
export const iconBattery = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 11v2"/><path d="M6 11h4M10 9v6"/></svg>`;

// ─── Braking System ─────────────────────────────────────────────────────────

/** Brake disc + caliper — custom SVG */
export const iconBrakeDisc = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="9"/>
      <circle cx="12" cy="12" r="4"/>
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/>
      <line x1="12" y1="3" x2="12" y2="8"/>
      <line x1="12" y1="16" x2="12" y2="21"/>
      <line x1="3" y1="12" x2="8" y2="12"/>
      <line x1="16" y1="12" x2="21" y2="12"/>
      <rect x="1.5" y="9.5" width="4" height="5" rx="1.5" fill="currentColor" stroke="none" opacity="0.7"/>
    </svg>`;

/** Brake pad — stylized rectangle with friction lines */
export const iconBrakePad = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="6" width="16" height="12" rx="3"/>
      <line x1="8" y1="10" x2="8" y2="14"/>
      <line x1="12" y1="10" x2="12" y2="14"/>
      <line x1="16" y1="10" x2="16" y2="14"/>
      <line x1="4" y1="18" x2="20" y2="18"/>
    </svg>`;

// ─── Tyre ──────────────────────────────────────────────────────────────────

/** Tyre cross-section — clean concentric circles with tread marks */
export const iconTyre = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="2" x2="12" y2="7"/>
      <line x1="12" y1="17" x2="12" y2="22"/>
      <line x1="2" y1="12" x2="7" y2="12"/>
      <line x1="17" y1="12" x2="22" y2="12"/>
      <line x1="4.93" y1="4.93" x2="8.46" y2="8.46"/>
      <line x1="15.54" y1="15.54" x2="19.07" y2="19.07"/>
      <line x1="19.07" y1="4.93" x2="15.54" y2="8.46"/>
      <line x1="8.46" y1="15.54" x2="4.93" y2="19.07"/>
    </svg>`;

// ─── Impact / Collision Icons ───────────────────────────────────────────────

/** General collision — two cars meeting head-on from diagonal */
export const iconCollision = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 10h4l2-3h4l2 3h3a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-1l-1 1.5H15v-1h-6v1H7.5L6.5 14H5a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1z" opacity="0.5" transform="translate(12,12) scale(-0.7,0.7) translate(-12,-12)"/>
      <path d="M3 10h4l2-3h4l2 3h3a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-1l-1 1.5H15v-1h-6v1H7.5L6.5 14H5a1 1 0 0 1-1-1v-2a1 1 0 0 1 1-1z"/>
      <line x1="11" y1="6" x2="11" y2="4" stroke-width="2.5"/>
      <line x1="13" y1="6" x2="15" y2="4" stroke-width="2.5"/>
      <line x1="9" y1="6" x2="7" y2="4" stroke-width="2.5"/>
    </svg>`;

/** Front impact — car facing arrows pointing into front */
export const iconFrontImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="9" width="14" height="8" rx="2"/>
      <path d="M4 11h-3M1 11l3-3M1 11l3 3"/>
      <circle cx="7.5" cy="17" r="1.5"/>
      <circle cx="14.5" cy="17" r="1.5"/>
      <path d="M10 9 L8 6 L14 6 L12 9"/>
    </svg>`;

/** Rear-end impact — arrow hitting car from behind */
export const iconRearImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="9" width="14" height="8" rx="2"/>
      <path d="M20 11h3M23 11l-3-3M23 11l-3 3"/>
      <circle cx="9.5" cy="17" r="1.5"/>
      <circle cx="16.5" cy="17" r="1.5"/>
      <path d="M14 9 L12 6 L18 6 L16 9"/>
    </svg>`;

/** Side impact — arrow hitting car from the side */
export const iconSideImpact = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="5" y="8" width="14" height="8" rx="2"/>
      <path d="M12 8V5M12 5l-3 3M12 5l3 3"/>
      <circle cx="8" cy="16" r="1.5"/>
      <circle cx="16" cy="16" r="1.5"/>
    </svg>`;

/** Rollover — car rotating */
export const iconRollover = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21.5 2v6h-6"/>
      <path d="M21.34 15.57a10 10 0 1 1-.57-8.38"/>
      <rect x="8" y="9" width="8" height="5" rx="1.5" transform="rotate(30 12 11.5)"/>
    </svg>`;

/** Pedestrian involved */
export const iconPedestrian = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="4" r="2"/>
      <path d="M10 22l1.5-6-2.5-3 3-4.5"/>
      <path d="M14 22l-1.5-6 2.5-3-3-4.5"/>
      <path d="M7 14l2-2"/>
      <path d="M17 14l-2-2"/>
    </svg>`;

// ─── AI / Intelligence ──────────────────────────────────────────────────────

/** AI sparkle — elegant AI indicator */
export const iconAI = (cls = 'w-4 h-4') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
    </svg>`;

// ─── Blackbox status ────────────────────────────────────────────────────────

/** Elegant tick in circle for blackbox active */
export const iconBlackboxActive = () =>
    `<span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-500/50"><svg class="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></span>`;

/** Elegant X in circle for no blackbox */
export const iconBlackboxNone = () =>
    `<span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-700/60 border border-slate-600/50"><svg class="w-3 h-3 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></span>`;

// ─── Manufacturer Logo Initials ─────────────────────────────────────────────

const MFR_COLORS = {
    BMW:        '#1C69D4',
    Mercedes:   '#B0B3B8',
    Audi:       '#BB0A21',
    Volkswagen: '#001E62',
    Fiat:       '#C8102E',
    Ferrari:    '#D40000',
    Lamborghini:'#DBA800',
    Porsche:    '#C0972A',
    Toyota:     '#CC0000',
    Ford:       '#003478',
    Opel:       '#FFC200',
    Renault:    '#EFDF00',
    Peugeot:    '#002D62',
    Alfa:       '#8C001A',
    Tesla:      '#CC0000',
    Volvo:      '#003057',
    Hyundai:    '#002C5F',
    Kia:        '#05141F',
};

const MFR_INITIALS = {
    BMW: 'BMW', Mercedes: 'MB', Audi: 'AU', Volkswagen: 'VW',
    Fiat: 'FI', Ferrari: 'FE', Lamborghini: 'LB', Porsche: 'P',
    Toyota: 'TY', Ford: 'FO', Opel: 'OP', Renault: 'RE',
    Peugeot: 'PG', 'Alfa Romeo': 'AR', Alfa: 'AR', Tesla: 'T',
    Volvo: 'VO', Hyundai: 'HY', Kia: 'KI',
};

export function manufacturerBadge(manufacturer, size = 'sm') {
    const key = Object.keys(MFR_INITIALS).find(k => manufacturer?.toLowerCase().includes(k.toLowerCase()));
    const initials = key ? MFR_INITIALS[key] : (manufacturer?.substring(0, 2).toUpperCase() || '??');
    const color = key ? MFR_COLORS[key] : '#475569';
    const dim = size === 'lg' ? 'w-9 h-9 text-[10px]' : 'w-6 h-6 text-[9px]';
    return `<span class="${dim} rounded-md flex items-center justify-center font-black tracking-tight text-white shrink-0" style="background:${color}22;border:1px solid ${color}55;color:${color}">${initials}</span>`;
}

// ─── Powertrain badge helper ────────────────────────────────────────────────

export function powertrainIcon(powertrain, cls = 'w-4 h-4') {
    if (!powertrain) return '';
    const pt = powertrain.toLowerCase();
    if (pt === 'electric') return `<span class="text-emerald-400" title="Electric">${iconElectric(cls)}</span>`;
    if (pt.includes('hybrid')) return `<span class="text-blue-400" title="Hybrid">${iconHybrid(cls)}</span>`;
    return `<span class="text-slate-400" title="Petrol/Diesel">${iconPetrol(cls)}</span>`;
}

// ─── Incident type icons ────────────────────────────────────────────────────

export function incidentIcon(type, cls = 'w-4 h-4') {
    const map = {
        collision:    iconCollision,
        rear_end:     iconRearImpact,
        side_impact:  iconSideImpact,
        rollover:     iconRollover,
        pedestrian:   iconPedestrian,
    };
    const fn = map[type] || iconCollision;
    return fn(cls);
}

// ─── Component icons ────────────────────────────────────────────────────────

export function componentIcon(category, cls = 'w-4 h-4') {
    if (category === 'tire') return iconTyre(cls);
    if (category === 'brake_pad') return iconBrakePad(cls);
    if (category === 'brake_disc') return iconBrakeDisc(cls);
    if (category === 'ev_battery') return iconBattery(cls);
    // fallback
    return `<i data-lucide="settings-2" class="${cls}"></i>`;
}
