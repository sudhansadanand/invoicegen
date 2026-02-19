import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "BillThis – Free GST Invoice Generator for Indian Businesses",
  description:
    "Create professional GST-compliant invoices in seconds. Free, simple, and built for Indian businesses.",
};

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
      "Amounts are formatted with the Indian numbering system (lakhs, crores) automatically.",
  },
  {
    icon: "📄",
    title: "Professional layout",
    description:
      "Clean, professional invoice layout your clients will trust — ready to print or email.",
  },
  {
    icon: "🆓",
    title: "Completely free",
    description:
      "No sign-up, no subscription, no watermarks. Just open the app and start billing.",
  },
];

const steps = [
  {
    num: "01",
    title: "Enter your business details",
    description:
      "Add your business name, address, GSTIN, and contact information in the 'From' section.",
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

export default function Home() {
  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans">
      {/* Nav */}
      <nav className="border-b border-slate-100 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <span className="text-xl font-bold tracking-tight text-slate-900">
            bill<span className="text-indigo-600">this</span>
          </span>
          <a
            href="#get-started"
            className="text-sm font-medium bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Create Invoice
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="px-6 pt-24 pb-20 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-sm font-medium px-3 py-1 rounded-full mb-6">
            <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
            Free · No sign-up required
          </div>
          <h1 className="text-5xl font-bold leading-tight tracking-tight text-slate-900 mb-6">
            GST invoices in{" "}
            <span className="text-indigo-600">seconds</span>,<br />
            not spreadsheets
          </h1>
          <p className="text-xl text-slate-500 leading-relaxed mb-10 max-w-2xl mx-auto">
            BillThis is a free, no-fuss invoice generator built for Indian
            businesses. Create GST-compliant PDF invoices without any
            sign-up or subscription.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center" id="get-started">
            <a
              href="https://billthis.streamlit.app"
              className="bg-indigo-600 text-white text-base font-semibold px-8 py-3.5 rounded-xl hover:bg-indigo-700 transition-colors shadow-sm"
            >
              Create your invoice →
            </a>
            <a
              href="#how-it-works"
              className="bg-slate-50 text-slate-700 text-base font-semibold px-8 py-3.5 rounded-xl hover:bg-slate-100 transition-colors border border-slate-200"
            >
              See how it works
            </a>
          </div>
        </div>

        {/* Mock invoice card */}
        <div className="max-w-2xl mx-auto mt-16 bg-white border border-slate-200 rounded-2xl shadow-lg overflow-hidden text-left">
          <div className="bg-slate-50 border-b border-slate-200 px-6 py-3 flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <div className="w-3 h-3 rounded-full bg-green-400"></div>
            <span className="ml-3 text-xs text-slate-400 font-mono">
              tax-invoice-896754.pdf
            </span>
          </div>
          <div className="px-8 py-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">From</p>
                <p className="font-semibold text-slate-800">Ship Gifts Online</p>
                <p className="text-sm text-slate-500">Chennai, Tamil Nadu</p>
                <p className="text-sm text-slate-500">GSTIN: 33ABCDE1234F1Z5</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Invoice</p>
                <p className="font-semibold text-slate-800">#896754</p>
                <p className="text-sm text-slate-500">19 Feb 2026</p>
              </div>
            </div>
            <table className="w-full text-sm mb-4">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="text-left pb-2">Description</th>
                  <th className="text-right pb-2">Qty</th>
                  <th className="text-right pb-2">Rate</th>
                  <th className="text-right pb-2">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {[
                  ["Premium Gift Box", "2", "₹1,250", "₹2,500"],
                  ["Custom Ribbon", "5", "₹80", "₹400"],
                  ["Greeting Card", "2", "₹50", "₹100"],
                ].map(([desc, qty, rate, amt]) => (
                  <tr key={desc} className="text-slate-700">
                    <td className="py-2">{desc}</td>
                    <td className="py-2 text-right">{qty}</td>
                    <td className="py-2 text-right">{rate}</td>
                    <td className="py-2 text-right">{amt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="border-t border-slate-200 pt-3 space-y-1 text-sm text-right">
              <div className="flex justify-between text-slate-500">
                <span>CGST 9%</span><span>₹270</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>SGST 9%</span><span>₹270</span>
              </div>
              <div className="flex justify-between font-semibold text-slate-900 text-base pt-1 border-t border-slate-200 mt-1">
                <span>Total</span><span>₹3,540</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-3">
            Everything you need to bill clients
          </h2>
          <p className="text-center text-slate-500 mb-12 max-w-xl mx-auto">
            No bloat, no subscriptions — just the features that matter for
            creating professional Indian tax invoices.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-sm transition-shadow"
              >
                <div className="text-2xl mb-3">{f.icon}</div>
                <h3 className="font-semibold text-slate-900 mb-2">{f.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {f.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-20" id="how-it-works">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-3">
            How it works
          </h2>
          <p className="text-center text-slate-500 mb-12">
            Four simple steps from blank form to PDF invoice.
          </p>
          <div className="space-y-8">
            {steps.map((step, i) => (
              <div key={step.num} className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center font-bold text-sm">
                  {step.num}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">
                    {step.title}
                  </h3>
                  <p className="text-slate-500 text-sm leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20 bg-indigo-600">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start billing in seconds
          </h2>
          <p className="text-indigo-200 mb-8 text-lg">
            No account needed. Open the app, fill in the details, download
            your invoice. It's that simple.
          </p>
          <a
            href="https://billthis.streamlit.app"
            className="inline-block bg-white text-indigo-600 text-base font-semibold px-8 py-3.5 rounded-xl hover:bg-indigo-50 transition-colors shadow-sm"
          >
            Create invoice for free →
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-100 px-6 py-8 text-center text-sm text-slate-400">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <span className="font-semibold text-slate-600">
            bill<span className="text-indigo-600">this</span>.in
          </span>
          <span>Free GST invoice generator for Indian businesses</span>
          <span>© {new Date().getFullYear()} BillThis</span>
        </div>
      </footer>
    </div>
  );
}
