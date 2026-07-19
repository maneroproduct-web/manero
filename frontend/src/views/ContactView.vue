<script setup lang="ts">
import { reactive, ref } from 'vue'

import { api } from '@/api/client'
// All copy and contact details live in content/contact.ts. See EDITING.md.
import { channels, faqs, form as formCopy, hero, subjects } from '@/content/contact'

const fields = reactive({
  name: '',
  email: '',
  phone: '',
  subject: 'general',
  message: '',
})

type FieldName = keyof typeof fields
const errors = reactive<Partial<Record<FieldName, string>>>({})

const sending = ref(false)
const sendError = ref<string | null>(null)
const reference = ref<string | null>(null)
const openFaq = ref<number | null>(0)

/** Mirrors the Pydantic rules in schemas/contact.py; the server re-checks. */
function validate(): boolean {
  for (const key of Object.keys(errors) as FieldName[]) delete errors[key]

  if (fields.name.trim().length < 2) errors.name = 'Please tell us your name'
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(fields.email)) {
    errors.email = 'Enter a valid email address — it is where we reply'
  }
  // Phone is optional, but must be plausible if given.
  const phone = fields.phone.replace(/^\+91/, '').replace(/[\s-]/g, '')
  if (phone && !/^\d{10}$/.test(phone)) {
    errors.phone = 'Enter a 10-digit mobile number, or leave it blank'
  }
  if (fields.message.trim().length < 10) {
    errors.message = 'A little more detail will help us answer properly'
  }

  return Object.keys(errors).length === 0
}

async function submit() {
  sendError.value = null
  if (!validate()) return

  sending.value = true
  try {
    const result = await api.sendContactMessage({
      name: fields.name.trim(),
      email: fields.email.trim(),
      phone: fields.phone.replace(/^\+91/, '').replace(/[\s-]/g, ''),
      subject: fields.subject,
      message: fields.message.trim(),
    })
    reference.value = result.reference
  } catch (err) {
    sendError.value =
      err instanceof Error ? err.message : 'Could not send your message just now.'
  } finally {
    sending.value = false
  }
}

function sendAnother() {
  reference.value = null
  fields.name = ''
  fields.email = ''
  fields.phone = ''
  fields.subject = 'general'
  fields.message = ''
}

const toggleFaq = (i: number) => (openFaq.value = openFaq.value === i ? null : i)
</script>

<template>
  <section class="hero">
    <div class="container">
      <p class="eyebrow">{{ hero.eyebrow }}</p>
      <h1>{{ hero.title }}</h1>
      <p class="lede">{{ hero.lede }}</p>
    </div>
  </section>

  <!-- Ways to reach us -->
  <section class="container channels">
    <component
      :is="channel.href ? 'a' : 'div'"
      v-for="channel in channels"
      :key="channel.label"
      :href="channel.href ?? undefined"
      :target="channel.href?.startsWith('http') ? '_blank' : undefined"
      :rel="channel.href?.startsWith('http') ? 'noopener noreferrer' : undefined"
      class="channel"
      :class="{ clickable: channel.href }"
    >
      <span class="channel-icon" aria-hidden="true">{{ channel.icon }}</span>
      <p class="channel-label">{{ channel.label }}</p>
      <p class="channel-value">{{ channel.value }}</p>
      <p class="channel-note">{{ channel.note }}</p>
    </component>
  </section>

  <!-- Form + FAQ -->
  <section class="container layout">
    <div class="panel">
      <template v-if="reference">
        <div class="success">
          <p class="success-mark" aria-hidden="true">✓</p>
          <h2>{{ formCopy.successTitle }}</h2>
          <p class="success-body">{{ formCopy.successBody }}</p>
          <p class="success-ref">
            Reference <strong>{{ reference }}</strong>
          </p>
          <button class="btn btn-outline" @click="sendAnother">
            Send another message
          </button>
        </div>
      </template>

      <template v-else>
        <h2>{{ formCopy.title }}</h2>
        <p class="panel-intro">{{ formCopy.intro }}</p>

        <p v-if="sendError" class="notice notice-error">{{ sendError }}</p>

        <form novalidate @submit.prevent="submit">
          <div class="row-2">
            <div class="field">
              <label for="c-name">Your name</label>
              <input
                id="c-name"
                v-model="fields.name"
                autocomplete="name"
                :aria-invalid="Boolean(errors.name)"
              />
              <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
            </div>
            <div class="field">
              <label for="c-email">Email</label>
              <input
                id="c-email"
                v-model="fields.email"
                type="email"
                autocomplete="email"
                placeholder="you@example.com"
                :aria-invalid="Boolean(errors.email)"
              />
              <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
            </div>
          </div>

          <div class="row-2">
            <div class="field">
              <label for="c-phone">Phone <span class="optional">(optional)</span></label>
              <input
                id="c-phone"
                v-model="fields.phone"
                type="tel"
                autocomplete="tel"
                placeholder="9876543210"
                :aria-invalid="Boolean(errors.phone)"
              />
              <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
            </div>
            <div class="field">
              <label for="c-subject">What is this about?</label>
              <select id="c-subject" v-model="fields.subject">
                <option v-for="s in subjects" :key="s.value" :value="s.value">
                  {{ s.label }}
                </option>
              </select>
            </div>
          </div>

          <div class="field">
            <label for="c-message">Message</label>
            <textarea
              id="c-message"
              v-model="fields.message"
              rows="6"
              :aria-invalid="Boolean(errors.message)"
            ></textarea>
            <span v-if="errors.message" class="field-error">{{ errors.message }}</span>
          </div>

          <button type="submit" class="btn btn-primary btn-block" :disabled="sending">
            {{ sending ? 'Sending…' : 'Send message' }}
          </button>
        </form>
      </template>
    </div>

    <aside class="faq">
      <h2>Common questions</h2>
      <div v-for="(faq, i) in faqs" :key="faq.q" class="faq-item">
        <button
          class="faq-q"
          :aria-expanded="openFaq === i"
          :aria-controls="`faq-body-${i}`"
          @click="toggleFaq(i)"
        >
          <span>{{ faq.q }}</span>
          <span class="faq-toggle" aria-hidden="true">{{ openFaq === i ? '−' : '+' }}</span>
        </button>
        <p v-show="openFaq === i" :id="`faq-body-${i}`" class="faq-a">{{ faq.a }}</p>
      </div>
    </aside>
  </section>
</template>

<style scoped>
/* ---------- Hero ---------- */

.hero {
  background: linear-gradient(165deg, #0d0b09 0%, #1c1713 55%, #241d16 100%);
  color: var(--crema-light);
  padding: 72px 0 80px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
}

.hero h1 {
  background: linear-gradient(180deg, #f6e27a 0%, #d4af37 45%, #b8860b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: clamp(2.1rem, 5vw, 3.2rem);
  margin: 0 0 18px;
}

.lede {
  max-width: 54ch;
  font-size: 1.02rem;
  line-height: 1.7;
  color: var(--crema-light);
  margin: 0;
}

/* ---------- Channels ---------- */

.channels {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: -38px;
  position: relative;
  z-index: 1;
}

.channel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px 20px;
  box-shadow: var(--shadow-sm);
  display: block;
}

.channel.clickable {
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}

.channel.clickable:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
  border-color: var(--gold);
}

.channel-icon {
  font-size: 1.4rem;
  display: block;
  margin-bottom: 10px;
}

.channel-label {
  margin: 0 0 5px;
  font-size: 0.72rem;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--ink-soft);
}

.channel-value {
  margin: 0 0 7px;
  font-weight: 600;
  color: var(--espresso);
  line-height: 1.45;
  /* The roastery address carries newlines in the content file. */
  white-space: pre-line;
  font-size: 0.95rem;
}

.channel-note {
  margin: 0;
  font-size: 0.8rem;
  color: var(--ink-soft);
}

/* ---------- Layout ---------- */

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
  gap: 32px;
  align-items: start;
  padding-top: 64px;
  padding-bottom: 80px;
}

.panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 30px;
}

.panel h2 {
  font-size: 1.35rem;
  margin-bottom: 6px;
}

.panel-intro {
  margin: 0 0 24px;
  color: var(--ink-soft);
  font-size: 0.93rem;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.optional {
  font-weight: 400;
  color: var(--ink-soft);
  text-transform: none;
  letter-spacing: 0;
}

textarea {
  padding: 11px 13px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  color: var(--ink);
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
}

textarea:focus {
  outline: 2px solid var(--gold);
  outline-offset: -1px;
  border-color: var(--gold);
}

textarea[aria-invalid='true'] {
  border-color: var(--danger);
}

form .btn {
  margin-top: 6px;
}

/* ---------- Success ---------- */

.success {
  text-align: center;
  padding: 26px 8px;
}

.success-mark {
  width: 50px;
  height: 50px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: var(--success);
  color: #fff;
  font-size: 1.4rem;
  display: grid;
  place-items: center;
}

.success h2 {
  margin-bottom: 10px;
}

.success-body {
  color: var(--ink-soft);
  line-height: 1.7;
  max-width: 42ch;
  margin: 0 auto 16px;
}

.success-ref {
  font-size: 0.86rem;
  color: var(--ink-soft);
  margin: 0 0 22px;
}

/* ---------- FAQ ---------- */

.faq {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 30px 26px;
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.faq h2 {
  font-size: 1.2rem;
  margin-bottom: 16px;
}

.faq-item {
  border-top: 1px solid var(--line);
}

.faq-item:first-of-type {
  border-top: none;
}

.faq-q {
  width: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 15px 0;
  background: none;
  border: none;
  text-align: left;
  font-size: 0.94rem;
  font-weight: 600;
  color: var(--espresso);
  line-height: 1.45;
}

.faq-q:hover {
  color: var(--accent);
}

.faq-toggle {
  font-size: 1.15rem;
  color: var(--gold-dark);
  line-height: 1;
  flex-shrink: 0;
}

.faq-a {
  margin: -4px 0 16px;
  padding-right: 24px;
  color: var(--ink-soft);
  font-size: 0.9rem;
  line-height: 1.75;
}

/* ---------- Responsive ---------- */

@media (max-width: 1000px) {
  .channels {
    grid-template-columns: repeat(2, 1fr);
  }
  .layout {
    grid-template-columns: 1fr;
  }
  .faq {
    position: static;
  }
}

@media (max-width: 560px) {
  .hero {
    padding: 52px 0 64px;
  }
  .channels {
    grid-template-columns: 1fr;
  }
  .row-2 {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .panel {
    padding: 24px 20px;
  }
}
</style>
