<script setup lang="ts">
import { computed } from 'vue'

// One view serves all four policies; the slug in the URL picks which.
// Content lives in content/policies.ts — see EDITING.md.
import { legalEntity, policies, policyBySlug } from '@/content/policies'

const props = defineProps<{ slug: string }>()

const policy = computed(() => policyBySlug(props.slug))
const others = computed(() => policies.filter((p) => p.slug !== props.slug))

/** A paragraph beginning "- " is rendered as a bullet. */
const isBullet = (line: string) => line.startsWith('- ')
const bulletText = (line: string) => line.slice(2)
</script>

<template>
  <div v-if="!policy" class="container page missing">
    <h1>Policy not found</h1>
    <p>That page does not exist.</p>
    <RouterLink to="/" class="btn btn-dark">Go home</RouterLink>
  </div>

  <template v-else>
    <section class="hero">
      <div class="container">
        <p class="eyebrow">Legal</p>
        <h1>{{ policy.title }}</h1>
        <p class="updated">Last updated {{ policy.updated }}</p>
      </div>
    </section>

    <div class="container layout">
      <article class="doc">
        <div class="draft-note">
          <strong>Placeholder document.</strong> This text has not been reviewed
          by a lawyer and contains invented details in [square brackets].
          Replace it before taking real orders.
        </div>

        <p v-if="policy.intro" class="intro">{{ policy.intro }}</p>

        <section v-for="section in policy.sections" :key="section.heading" class="sec">
          <h2>{{ section.heading }}</h2>
          <template v-for="(line, i) in section.body" :key="i">
            <ul v-if="isBullet(line)" class="bullets">
              <li>{{ bulletText(line) }}</li>
            </ul>
            <p v-else>{{ line }}</p>
          </template>
        </section>

        <footer class="doc-foot">
          <h2>Contact</h2>
          <p>
            {{ legalEntity.name }}<br />
            {{ legalEntity.address }}<br />
            GSTIN {{ legalEntity.gstin }}
          </p>
          <p>
            <a :href="`mailto:${legalEntity.email}`">{{ legalEntity.email }}</a>
            &nbsp;·&nbsp;
            <a :href="`tel:${legalEntity.phone.replace(/\s/g, '')}`">
              {{ legalEntity.phone }}
            </a>
          </p>
        </footer>
      </article>

      <aside class="side">
        <h2>Other policies</h2>
        <RouterLink
          v-for="other in others"
          :key="other.slug"
          :to="`/policies/${other.slug}`"
          class="side-link"
        >
          {{ other.title }}
        </RouterLink>
        <RouterLink to="/contact" class="side-link contact">
          Still have a question?
        </RouterLink>
      </aside>
    </div>
  </template>
</template>

<style scoped>
.hero {
  background: linear-gradient(165deg, #0d0b09 0%, #1c1713 100%);
  color: var(--crema-light);
  padding: 56px 0 60px;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 0.74rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
}

.hero h1 {
  color: var(--gold-light);
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  margin: 0 0 10px;
}

.updated {
  margin: 0;
  font-size: 0.85rem;
  color: var(--crema);
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 250px;
  gap: 40px;
  align-items: start;
  padding-top: 48px;
  padding-bottom: 80px;
}

.doc {
  max-width: 72ch;
}

.draft-note {
  background: #fdf6e8;
  border: 1px solid #ecd9ab;
  border-radius: var(--radius);
  padding: 13px 15px;
  font-size: 0.85rem;
  color: #7a5c12;
  line-height: 1.6;
  margin-bottom: 28px;
}

.intro {
  font-size: 1.02rem;
  line-height: 1.8;
  color: var(--ink);
  margin: 0 0 32px;
}

.sec {
  margin-bottom: 30px;
}

.sec h2 {
  font-size: 1.12rem;
  margin: 0 0 12px;
}

.sec p {
  margin: 0 0 13px;
  color: var(--ink-soft);
  line-height: 1.8;
  font-size: 0.94rem;
}

.bullets {
  margin: 0 0 13px;
  padding-left: 20px;
}

.bullets li {
  color: var(--ink-soft);
  line-height: 1.8;
  font-size: 0.94rem;
  margin-bottom: 5px;
}

.doc-foot {
  margin-top: 44px;
  padding-top: 26px;
  border-top: 1px solid var(--line);
}

.doc-foot h2 {
  font-size: 1.05rem;
  margin-bottom: 12px;
}

.doc-foot p {
  color: var(--ink-soft);
  line-height: 1.8;
  font-size: 0.92rem;
  margin: 0 0 10px;
}

.doc-foot a {
  color: var(--accent);
  text-decoration: underline;
}

.side {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.side h2 {
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.side-link {
  display: block;
  padding: 10px 0;
  font-size: 0.9rem;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--line);
}

.side-link:last-child {
  border-bottom: none;
}

.side-link:hover {
  color: var(--accent);
}

.side-link.contact {
  color: var(--accent);
  font-weight: 600;
}

.missing {
  text-align: center;
  padding: 80px 20px;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  .side {
    position: static;
  }
}

@media (max-width: 900px), (pointer: coarse) {
  .side-link {
    padding: 13px 0;
  }
}
</style>
