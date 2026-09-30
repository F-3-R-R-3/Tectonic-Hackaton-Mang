const base = {
  width: 20,
  height: 20,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.9,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
}

function Svg({ children, size = 20, ...rest }) {
  return (
    <svg {...base} width={size} height={size} {...rest} aria-hidden="true">
      {children}
    </svg>
  )
}

export const IconSignal = (p) => (
  <Svg {...p}>
    <path d="M3 12h3l3-8 3 16 3-11 2 3h4" />
  </Svg>
)

export const IconProblem = (p) => (
  <Svg {...p}>
    <path d="M12 9v4M12 17h.01" />
    <path d="M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
  </Svg>
)

export const IconSolution = (p) => (
  <Svg {...p}>
    <path d="M9 18h6M10 22h4" />
    <path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2V17h6v-.3c0-.8.4-1.5 1-2A7 7 0 0 0 12 2Z" />
  </Svg>
)

export const IconArrowRight = (p) => (
  <Svg {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </Svg>
)

export const IconArrowLeft = (p) => (
  <Svg {...p}>
    <path d="M19 12H5M11 18l-6-6 6-6" />
  </Svg>
)

export const IconCheck = (p) => (
  <Svg {...p}>
    <path d="M20 6 9 17l-5-5" />
  </Svg>
)

export const IconWallet = (p) => (
  <Svg {...p}>
    <path d="M3 7a2 2 0 0 1 2-2h13a1 1 0 0 1 1 1v2" />
    <path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2H5a2 2 0 0 1-2-2Z" />
    <path d="M16 13h.01" />
  </Svg>
)

export const IconCar = (p) => (
  <Svg {...p}>
    <path d="M5 13 6.6 8.4A2 2 0 0 1 8.5 7h7a2 2 0 0 1 1.9 1.4L19 13" />
    <path d="M3 13h18v4a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-1H6v1a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-4Z" />
    <path d="M7 16h.01M17 16h.01" />
  </Svg>
)

export const IconPiggy = (p) => (
  <Svg {...p}>
    <path d="M19 11a5 5 0 0 0-5-5H8a5 5 0 0 0-5 5v2a3 3 0 0 0 3 3v2h3v-2h3v2h3v-2.3A5 5 0 0 0 19 13Z" />
    <path d="M16 11h.01M7 8.5A3 3 0 0 1 9 6" />
  </Svg>
)

export const IconDoc = (p) => (
  <Svg {...p}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z" />
    <path d="M14 3v5h5M9 13h6M9 17h4" />
  </Svg>
)

export const IconHome = (p) => (
  <Svg {...p}>
    <path d="M3 10.5 12 3l9 7.5" />
    <path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5" />
  </Svg>
)

export const IconCard = (p) => (
  <Svg {...p}>
    <rect x="3" y="5" width="18" height="14" rx="2" />
    <path d="M3 10h18M7 15h4" />
  </Svg>
)

export const IconSend = (p) => (
  <Svg {...p}>
    <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7Z" />
  </Svg>
)

export const IconShield = (p) => (
  <Svg {...p}>
    <path d="M12 3 5 6v6c0 4 3 7.4 7 9 4-1.6 7-5 7-9V6l-7-3Z" />
    <path d="m9 12 2 2 4-4" />
  </Svg>
)

export const IconSearch = (p) => (
  <Svg {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="m21 21-4.3-4.3" />
  </Svg>
)

export const IconBell = (p) => (
  <Svg {...p}>
    <path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" />
    <path d="M10.5 20a2 2 0 0 0 3 0" />
  </Svg>
)

export const IconSparkle = (p) => (
  <Svg {...p}>
    <path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" />
  </Svg>
)

export const IconMic = (p) => (
  <Svg {...p}>
    <rect x="9" y="3" width="6" height="11" rx="3" />
    <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
  </Svg>
)

export const IconMenu = (p) => (
  <Svg {...p}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </Svg>
)

export const IconClose = (p) => (
  <Svg {...p}>
    <path d="M6 6l12 12M18 6 6 18" />
  </Svg>
)

export const IconTrendUp = (p) => (
  <Svg {...p}>
    <path d="M3 17 9 11l4 4 8-8" />
    <path d="M15 7h6v6" />
  </Svg>
)

export const IconEuro = (p) => (
  <Svg {...p}>
    <path d="M18 7a7 7 0 1 0 0 10" />
    <path d="M4 10h9M4 14h9" />
  </Svg>
)

const CATEGORY_ICONS = {
  slapend_geld: IconWallet,
  mobiliteit: IconCar,
  sparen: IconPiggy,
  administratie: IconDoc,
}

export function categoryIcon(category) {
  return CATEGORY_ICONS[category] ?? IconSparkle
}
