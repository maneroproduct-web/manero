<script setup lang="ts">
// All copy lives in content/story.ts so it can be rewritten without touching
// this file. See EDITING.md.
import {
  closing,
  commitments,
  hero,
  origin,
  process,
  stats,
  values,
} from '@/content/story'
</script>

<template>
  <!-- Hero -->
  <section class="hero">
    <div class="container hero-inner">
      <p class="eyebrow">{{ hero.eyebrow }}</p>
      <h1>{{ hero.title }}</h1>
      <p class="lede">{{ hero.lede }}</p>
    </div>
  </section>

  <!-- Origin story -->
  <section class="container origin">
    <div class="origin-media">
      <img :src="origin.image" :alt="origin.imageAlt" loading="lazy" />
    </div>
    <div class="origin-copy">
      <h2>{{ origin.title }}</h2>
      <p v-for="(para, i) in origin.paragraphs" :key="i">{{ para }}</p>
      <blockquote>{{ origin.pullQuote }}</blockquote>
    </div>
  </section>

  <!-- Stats strip -->
  <section class="stats">
    <div class="container stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat">
        <p class="stat-value">{{ stat.value }}</p>
        <p class="stat-label">{{ stat.label }}</p>
      </div>
    </div>
  </section>

  <!-- Values -->
  <section class="container block">
    <h2 class="centred">How we do it differently</h2>
    <div class="values">
      <article v-for="value in values" :key="value.title" class="value">
        <span class="value-icon" aria-hidden="true">{{ value.icon }}</span>
        <h3>{{ value.title }}</h3>
        <p>{{ value.body }}</p>
      </article>
    </div>
  </section>

  <!-- Process -->
  <section class="process">
    <div class="container">
      <h2 class="centred light">From cherry to cup</h2>
      <ol class="steps">
        <li v-for="item in process" :key="item.step" class="step">
          <span class="step-num">{{ item.step }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.body }}</p>
        </li>
      </ol>
    </div>
  </section>

  <!-- Commitments -->
  <section class="container block">
    <div class="commit-head">
      <h2>{{ commitments.title }}</h2>
      <p class="commit-intro">{{ commitments.intro }}</p>
    </div>
    <div class="commitments">
      <article v-for="item in commitments.items" :key="item.title" class="commitment">
        <h3>{{ item.title }}</h3>
        <p>{{ item.body }}</p>
      </article>
    </div>
  </section>

  <!-- Closing CTA -->
  <section class="closing">
    <div class="container closing-inner">
      <h2>{{ closing.title }}</h2>
      <p>{{ closing.body }}</p>
      <div class="cta">
        <RouterLink to="/shop" class="btn btn-primary">
          {{ closing.primaryLabel }}
        </RouterLink>
        <RouterLink to="/contact" class="btn btn-outline light">
          {{ closing.secondaryLabel }}
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ---------- Hero ---------- */

.hero {
  background: linear-gradient(165deg, #0d0b09 0%, #1c1713 55%, #241d16 100%);
  color: var(--crema-light);
  padding: 84px 0 92px;
}

.eyebrow {
  margin: 0 0 14px;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
}

.hero h1 {
  /* white-space: pre-line honours the \n in the content file, so the headline
     breaks where the copy says it should. */
  white-space: pre-line;
  background: linear-gradient(180deg, #f6e27a 0%, #d4af37 45%, #b8860b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: clamp(2.1rem, 5vw, 3.4rem);
  margin: 0 0 22px;
}

.lede {
  max-width: 58ch;
  font-size: 1.04rem;
  line-height: 1.7;
  color: var(--crema-light);
  margin: 0;
}

/* ---------- Origin ---------- */

.origin {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.1fr);
  gap: 52px;
  align-items: center;
  padding-top: 72px;
  padding-bottom: 72px;
}

.origin-media img {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  border-radius: var(--radius-lg);
}

.origin-copy h2 {
  font-size: 1.9rem;
  margin-bottom: 20px;
}

.origin-copy p {
  color: var(--ink-soft);
  line-height: 1.8;
  margin: 0 0 18px;
}

blockquote {
  margin: 28px 0 0;
  padding: 18px 0 18px 24px;
  border-left: 3px solid var(--gold);
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.22rem;
  line-height: 1.5;
  color: var(--espresso);
  font-style: italic;
}

/* ---------- Stats ---------- */

.stats {
  background: var(--espresso);
  padding: 44px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
  text-align: center;
}

.stat-value {
  margin: 0 0 4px;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 2rem;
  font-weight: 600;
  color: var(--gold);
}

.stat-label {
  margin: 0;
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--crema);
}

/* ---------- Shared block ---------- */

.block {
  padding-top: 76px;
  padding-bottom: 76px;
}

.centred {
  text-align: center;
  font-size: 1.9rem;
  margin-bottom: 40px;
}

.centred.light {
  color: var(--gold-light);
}

/* ---------- Values ---------- */

.values {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.value {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 30px 26px;
}

.value-icon {
  font-size: 1.8rem;
  display: block;
  margin-bottom: 14px;
}

.value h3 {
  font-size: 1.1rem;
  margin-bottom: 10px;
}

.value p {
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.7;
  font-size: 0.93rem;
}

/* ---------- Process ---------- */

.process {
  background: var(--espresso);
  padding: 76px 0;
}

.steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 26px;
}

.step {
  border-top: 1px solid rgba(212, 175, 55, 0.3);
  padding-top: 20px;
}

.step-num {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.5rem;
  color: var(--gold);
  display: block;
  margin-bottom: 10px;
}

.step h3 {
  color: var(--gold-light);
  font-size: 1.02rem;
  margin-bottom: 9px;
}

.step p {
  margin: 0;
  color: var(--crema);
  font-size: 0.89rem;
  line-height: 1.7;
}

/* ---------- Commitments ---------- */

.commit-head {
  max-width: 62ch;
  margin-bottom: 36px;
}

.commit-head h2 {
  font-size: 1.9rem;
}

.commit-intro {
  color: var(--ink-soft);
  line-height: 1.8;
  margin: 0;
}

.commitments {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.commitment {
  background: var(--paper);
  padding: 28px 24px;
}

.commitment h3 {
  font-size: 1.02rem;
  margin-bottom: 10px;
}

.commitment p {
  margin: 0;
  color: var(--ink-soft);
  line-height: 1.7;
  font-size: 0.91rem;
}

/* ---------- Closing ---------- */

.closing {
  background: linear-gradient(165deg, #1c1713 0%, #0d0b09 100%);
  padding: 76px 0;
  text-align: center;
}

.closing-inner h2 {
  color: var(--gold-light);
  font-size: 1.9rem;
}

.closing-inner p {
  max-width: 54ch;
  margin: 0 auto 30px;
  color: var(--crema);
  line-height: 1.8;
}

.cta {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-outline.light {
  color: var(--gold-light);
  border-color: rgba(212, 175, 55, 0.45);
}

.btn-outline.light:hover {
  background: rgba(212, 175, 55, 0.12);
  border-color: var(--gold);
}

/* ---------- Responsive ---------- */

@media (max-width: 960px) {
  .origin {
    grid-template-columns: 1fr;
    gap: 34px;
  }
  .origin-media img {
    aspect-ratio: 16 / 10;
  }
  .values,
  .commitments,
  .steps {
    grid-template-columns: repeat(2, 1fr);
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
  }
}

@media (max-width: 600px) {
  .hero {
    padding: 56px 0 64px;
  }
  .values,
  .commitments,
  .steps,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .block,
  .process,
  .closing {
    padding-top: 52px;
    padding-bottom: 52px;
  }
  .cta .btn {
    width: 100%;
  }
}
</style>
