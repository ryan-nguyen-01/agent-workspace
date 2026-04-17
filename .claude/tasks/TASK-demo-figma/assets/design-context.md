# Design Context — Home Page

> Extracted from Figma MCP `get_design_context`
> File: Fashion Ecommerce Store | Frame: Home (2:63) | 1440×3998px

## Source

- **Figma URL**: https://www.figma.com/design/7xrPkquBzkRr2HLgTMKqr8/Fashion-Ecommerce-Store?node-id=2-63
- **Extraction method**: `mcp_com_figma_mcp_get_design_context`
- **Output format**: React + Tailwind CSS (default từ MCP)

---

## Page Sections (top to bottom)

### 1. Header / Navigation (top: 50px)

```jsx
{/* Logo + Nav links */}
<div className="flex items-center">
  <p className="font-['Beatrice_Deck_Trial:Medium'] text-[16px] tracking-[2px]">Home</p>
  <p className="font-['Beatrice_Deck_Trial:Medium'] text-[16px] tracking-[2px]">Collections</p>
  <p className="font-['Beatrice_Deck_Trial:Medium'] text-[16px] tracking-[2px]">New</p>
</div>

{/* Right side: icons + Cart button */}
<div className="bg-black h-[50px] rounded-[22px] w-[76px]">
  <p className="font-['Beatrice_Deck_Trial:Medium'] text-[12px] text-white tracking-[2px]">Cart</p>
</div>
```

**Notes**: 3 icon groups (search, user, wishlist) + Cart CTA (rounded pill, black bg)

### 2. Category Menu (left sidebar, top: 156px)

```jsx
<div className="font-['Beatrice_Deck_Trial:Regular'] text-[16px] tracking-[2px]">
  <p>MEN</p>
  <p>WOMEN</p>
  <p>KIDS</p>
</div>
```

### 3. Search Bar (top: 242px)

```jsx
<div className="bg-[#d9d9d9] h-[50px] rounded-[2px] w-[367px]">
  <p className="font-['Beatrice_Deck_Trial:Regular'] text-[12px] text-[rgba(0,0,0,0.66)] tracking-[2px]">
    Search
  </p>
</div>
```

### 4. Hero Section (top: 386px)

```jsx
{/* Title */}
<div className="font-['Beatrice_Deck_Trial:Extrabold'] text-[48px] tracking-[2px] uppercase">
  <p>New</p>
  <p>Collection</p>
</div>

{/* Season label */}
<div className="font-['Beatrice_Deck_Trial:Regular'] text-[16px] tracking-[2px]">
  <p>Summer</p>
  <p>2024</p>
</div>

{/* CTA Button */}
<div className="bg-[#d9d9d9] h-[40px] w-[265px]">
  <p className="font-['Beatrice_Deck_Trial:Medium'] text-[16px]">Go To Shop</p>
</div>

{/* Product cards: 2 bordered images */}
<div className="border border-[#d7d7d7] h-[376px] w-[366px]">
  {/* Product image */}
</div>
```

### 5. "New This Week" Section (top: 912px)

```jsx
<div className="font-['Beatrice_Deck_Trial:Extrabold'] text-[48px] tracking-[2px] uppercase">
  <p>New</p>
  <p>This week</p>
</div>
<span className="text-[#000e8a] text-[20px]">(50)</span>  {/* Item count */}
```

**Product Grid**: 4 columns × product cards
- Each card: `border border-[#d7d7d7] h-[313px] w-[304px]`
- Wishlist icon overlay (34×34px)
- Labels: category (12px, opacity-66), title (14px), price ($99)
- Pagination arrows (left/right, 40×40px bordered)

### 6. "XIV Collections" Section (top: 1576px)

```jsx
<div className="font-['Beatrice_Deck_Trial:Extrabold'] text-[48px] tracking-[2px] uppercase">
  <p>XIV</p>
  <p>Collections</p>
  <p>23-24</p>
</div>
```

**Filter bar**: (All) | Men | Women | KID + Filters(+) / Sorts(-)
**Product grid**: 3 columns, same card pattern as section 5
**Pricing**: $199 each

### 7. "Our Approach" Section (top: 2480px)

```jsx
<p className="font-['Beatrice_Deck_Trial:Regular'] text-[48px] tracking-[2px] uppercase text-center">
  Our Approach to fashion design
</p>
```

**Gallery**: 4 overlapping bordered images (317×389-419px)

### 8. Footer (top: 3370px)

```text
Layout:
  Left column (16.67%): Info nav (Pricing, About, Contacts) + Languages (Eng, Esp, Sve)
  Right column (41.67%): Technologies (VR, XIV, QR) + social icon
  Bottom: © 2024 copyright | privacy | Terms

Typography:
  Section labels: Inter Medium 10px uppercase tracking-[0.4px] opacity-40
  Nav items: Inter Medium 12px uppercase opacity-60
  Tech headings: Inter Black 80px tracking-[-1.6px]
  NFC description: Inter Medium 12px opacity-40
```

---

## Key Components (reusable)

| Component | Size | Style |
|-----------|------|-------|
| Product Card (small) | 304×313px | `border border-[#d7d7d7]`, image overflow, wishlist icon |
| Product Card (large) | 366×376px | `border border-[#d7d7d7]`, image overflow |
| CTA Button | 265×40px | `bg-[#d9d9d9]`, left arrow icon + text |
| Cart Button | 76×50px | `bg-black rounded-[22px]`, white text |
| Nav Arrow | 40×40px | `border border-[#a3a3a3]`, rotate for direction |
| Search Bar | 367×50px | `bg-[#d9d9d9] rounded-[2px]`, search icon + placeholder |
| Gallery Image | 317×389-419px | `border border-[#d7d7d7]`, overlapping layout |

## Image Assets

> Full inventory with export instructions: `image-assets.yaml`

### Icons (export as SVG or use icon library)
| Node | Name | Size | Usage | Library Alternative |
|------|------|------|-------|-------------------|
| Group6 | logo | 120×40 | Header brand logo | None (custom, must export) |
| Vector | search | 24×24 | Header search bar | `lucide:Search` |
| Group8 | user-account | 24×24 | Header user link | `lucide:User` |
| Group9 | wishlist | 24×24 | Header wishlist link | `lucide:Heart` |
| Group45 | wishlist-overlay | 34×34 | ProductCard toggle | `lucide:Heart` (outlined/filled) |
| Vector | nav-arrows | 40×40 | Carousel prev/next | `lucide:ChevronLeft/Right` |
| ToTop | scroll-to-top | 48×48 | Fixed button | `lucide:ArrowUp` |

### Product Images (placeholders — use CMS/API images in production)
- `Rectangle12..15` → "New This Week" grid (304×313px, ratio 304:313)
- `Rectangle16..17` → "XIV Collections" carousel (366×376px)
- `Rectangle18..22` → "Our Approach" editorial layout (mixed sizes)

### Decorative (skip export — use CSS)
- `Line6`, `Line7` → Section dividers → `border-bottom: 1px solid #d7d7d7`

### Recommended approach
1. **Standard icons** → Use Lucide/Heroicons library (smaller bundle, no API call)
2. **Custom icons** (logo only) → Export SVG via Figma REST API
3. **Product images** → Dynamic from product API, NOT Figma export
4. **Dividers** → CSS borders, no image needed

### Export command (for custom icons)
```bash
# Export Group6 (logo) as SVG via Figma REST API
curl -H "X-FIGMA-TOKEN: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/images/7xrPkquBzkRr2HLgTMKqr8?ids=Group6&format=svg"
# Response: { "images": { "Group6": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/..." } }
# Download the URL and save to src/assets/icons/logo.svg
```
