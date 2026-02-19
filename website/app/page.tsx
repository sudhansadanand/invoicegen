const features = [
  {
    icon: "⚡",
    title: "Instant PDF invoices",
    description:
      "Fill in your details, add line items, and download a formatted PDF invoice in under a minute.",
  },
  {
    icon: "🧾",
    title: "GST-ready by default",
    description:
      "Built-in CGST & SGST fields with automatic tax calculations — fully compliant for Indian businesses.",
  },
  {
    icon: "🏢",
    title: "Sender & recipient details",
    description:
      "Store TIN, CST, and GST numbers for both parties. Everything you need on a legal tax invoice.",
  },
  {
    icon: "🔢",
    title: "Indian number formatting",
    description:
      "Amounts formatted with the Indian numbering system (lakhs, crores) automatically.",
  },
  {
    icon: "📄",
    title: "Professional layout",
    description:
      "Clean invoice layout your clients will trust — ready to print or send over email.",
  },
  {
    icon: "🆓",
    title: "Completely free",
    description:
      "No sign-up, no subscription, no watermarks. Open the app and start billing right away.",
  },
];

const steps = [
  {
    num: "01",
    title: "Enter your business details",
    description:
      "Add your business name, address, GSTIN, and contact info in the 'From' section.",
  },
  {
    num: "02",
    title: "Add your client details",
    description:
      "Fill in your client's information in the 'To' section. All GST fields supported.",
  },
  {
    num: "03",
    title: "Add line items",
    description:
      "List your products or services with quantity, unit, and price. Totals calculate automatically.",
  },
  {
    num: "04",
    title: "Download your invoice",
    description:
      "Click Generate and download your professionally formatted PDF invoice instantly.",
  },
];

const mockItems = [
  ["Premium Gift Box", "2", "₹1,250", "₹2,500"],
  ["Custom Ribbon", "5", "₹80", "₹400"],
  ["Greeting Card", "2", "₹50", "₹100"],
];

export default function Home() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* ── Nav ── */}
      <nav className="sticky top-0 z-50 border-b border-slate-100 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="text-xl font-extrabold tracking-tight">
            bill<span className="text-indigo-600">this</span>
          </span>
          <a
            href="#app"
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            Create Invoice
          </a>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="px-6 pb-20 pt-24 text-center">
        <div className="mx-auto max-w-3xl">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700">
            <span className="h-2 w-2 rounded-full bg-indigo-500" />
            Free · No sign-up required
          </div>

          <h1 className="mb-6 text-5xl font-extrabold leading-tight tracking-tight text-slate-900">
            GST invoices in{" "}
            <span className="text-indigo-600">seconds</span>,
            <br />
            not spreadsheets
          </h1>

          <p className="mx-auto mb-10 max-w-xl text-xl leading-relaxed text-slate-500">
            BillThis is a free, no-fuss invoice generator built for Indian
            SMBs. Create GST-compliant PDF invoices without any sign-up or
            subscription.
          </p>

          <div
            id="app"
            className="flex flex-wrap justify-center gap-3"
          >
            <a
              href="https://billthis.streamlit.app"
              className="rounded-xl bg-indigo-600 px-8 py-3.5 text-base font-semibold text-white shadow-sm transition hover:bg-indigo-700"
            >
              Create your invoice →
            </a>
            <a
              href="#how"
              className="rounded-xl border border-slate-200 bg-slate-50 px-8 py-3.5 text-base font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              See how it works
            </a>
          </div>
        </div>

        {/* Mock invoice preview */}
        <div className="mx-auto mt-16 max-w-2xl overflow-hidden rounded-2xl border border-slate-200 bg-white text-left shadow-xl">
          {/* Titlebar */}
          <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-6 py-3">
            <span className="h-3 w-3 rounded-full bg-red-400" />
            <span className="h-3 w-3 rounded-full bg-yellow-400" />
            <span className="h-3 w-3 rounded-full bg-green-400" />
            <span className="ml-3 font-mono text-xs text-slate-400">
              tax-invoice-896754.pdf
            </span>
          </div>

          {/* Body */}
          <div className="px-8 py-6">
            <div className="mb-6 flex justify-between">
              <div>
                <p className="mb-1 text-xs uppercase tracking-wider text-slate-400">
                  From
                </p>
                <p className="font-semibold text-slate-800">Ship Gifts Online</p>
                <p className="text-sm text-slate-500">Chennai, Tamil Nadu</p>
                <p className="text-sm text-slate-500">GSTIN: 33ABCDE1234F1Z5</p>
              </div>
              <div className="text-right">
                <p className="mb-1 text-xs uppercase tracking-wider text-slate-400">
                  Invoice
                </p>
                <p className="font-semibold text-slate-800">#896754</p>
                <p className="text-sm text-slate-500">19 Feb 2026</p>
              </div>
            </div>

            <table className="mb-4 w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wider text-slate-400">
                  <th className="pb-2 text-left">Description</th>
                  <th className="pb-2 text-right">Qty</th>
                  <th className="pb-2 text-right">Rate</th>
                  <th className="pb-2 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {mockItems.map(([desc, qty, rate, amt]) => (
                  <tr key={desc} className="text-slate-700">
                    <td className="py-2">{desc}</td>
                    <td className="py-2 text-right">{qty}</td>
                    <td className="py-2 text-right">{rate}</td>
                    <td className="py-2 text-right">{amt}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="space-y-1 border-t border-slate-200 pt-3 text-sm">
              <div className="flex justify-between text-slate-500">
                <span>CGST 9%</span>
                <span>₹270</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>SGST 9%</span>
                <span>₹270</span>
              </div>
              <div className="mt-1 flex justify-between border-t border-slate-200 pt-2 text-base font-bold text-slate-900">
                <span>Total</span>
                <span>₹3,540</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="bg-slate-50 px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-3 text-center text-3xl font-extrabold tracking-tight text-slate-900">
            Everything you need to bill clients
          </h2>
          <p className="mx-auto mb-12 max-w-xl text-center text-slate-500">
            No bloat, no subscriptions — just the features that matter for
            professional Indian tax invoices.
          </p>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-xl border border-slate-200 bg-white p-6 transition hover:shadow-md"
              >
                <div className="mb-3 text-2xl">{f.icon}</div>
                <h3 className="mb-1.5 font-bold text-slate-900">{f.title}</h3>
                <p className="text-sm leading-relaxed text-slate-500">
                  {f.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How it works ── */}
      <section className="px-6 py-20" id="how">
        <div className="mx-auto max-w-2xl">
          <h2 className="mb-3 text-center text-3xl font-extrabold tracking-tight text-slate-900">
            How it works
          </h2>
          <p className="mb-12 text-center text-slate-500">
            Four simple steps from blank form to PDF invoice.
          </p>
          <div className="space-y-8">
            {steps.map((step) => (
              <div key={step.num} className="flex items-start gap-5">
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-sm font-bold text-indigo-600">
                  {step.num}
                </div>
                <div>
                  <h3 className="mb-1 font-bold text-slate-900">{step.title}</h3>
                  <p className="text-sm leading-relaxed text-slate-500">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="bg-indigo-600 px-6 py-20 text-center">
        <div className="mx-auto max-w-xl">
          <h2 className="mb-4 text-3xl font-extrabold tracking-tight text-white">
            Start billing in seconds
          </h2>
          <p className="mb-8 text-lg text-indigo-200">
            No account needed. Open the app, fill in the details, download
            your invoice. It&apos;s that simple.
          </p>
          <a
            href="https://billthis.streamlit.app"
            className="inline-block rounded-xl bg-white px-8 py-3.5 text-base font-semibold text-indigo-600 shadow-sm transition hover:bg-indigo-50"
          >
            Create invoice for free →
          </a>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-slate-100 px-6 py-8">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-3 text-sm text-slate-400 sm:flex-row">
          <span className="font-bold text-slate-600">
            bill<span className="text-indigo-600">this</span>.in
          </span>
          <span>Free GST invoice generator for Indian businesses</span>
          <span>© {new Date().getFullYear()} BillThis</span>
        </div>
      </footer>
    </div>
  );
}
