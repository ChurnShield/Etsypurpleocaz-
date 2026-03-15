export const ETSY_CARD_SHADOW_PRESET = {
  shadow_color: "0,0,0",
  shadow_opacity: 0.75,
  shadow_blur: 12,
  shadow_offset_x: 15,
  shadow_offset_y: 15,
  padding: 40,
} as const;

export const ETSY_CARD_SHADOW_ANGLED_PRESET = {
  ...ETSY_CARD_SHADOW_PRESET,
  rotation_degrees: -5,
  padding: 60,
} as const;
