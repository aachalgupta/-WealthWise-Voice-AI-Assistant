"""
faq_data.py, 52 questions
WealthWise Advisory — FAQ Knowledge Base
Covers real queries Indian users ask a financial advisory firm.
Voicebot scope: company information + appointment booking only.
No financial advisory content. English only.
"""

faqs = [

    # ── COMPANY GENERAL ──────────────────────────────────
    {
        "question": "What is WealthWise Advisory?",
        "answer": "WealthWise Advisory is a SEBI-registered financial advisory firm based in Mumbai. We help individuals and families plan their finances, grow their wealth, and secure their future through personalised investment and financial planning services."
    },
    {
        "question": "Is WealthWise SEBI registered?",
        "answer": "Yes, WealthWise Advisory is registered with SEBI as a Registered Investment Advisor (RIA) under registration number INA000012345. You can verify this on the SEBI website."
    },
    {
        "question": "Where is WealthWise located?",
        "answer": "Our main office is in Bandra Kurla Complex, Mumbai. We also have offices in Pune, Bangalore, and Delhi. However, most of our advisory sessions are conducted online via video call, so you can connect with us from anywhere in India."
    },
    {
        "question": "How do I contact WealthWise?",
        "answer": "You can reach us at support@wealthwise.in or call our helpline at 1800-XXX-XXXX. You can also book an appointment directly through this voice assistant and one of our advisors will call you back."
    },
    {
        "question": "What are your working hours?",
        "answer": "Our advisors are available Monday to Saturday from 9 AM to 7 PM IST. You can book appointments during these hours. Our voice assistant is available 24 by 7 for queries and appointment booking."
    },
    {
        "question": "How many clients does WealthWise have?",
        "answer": "WealthWise Advisory currently serves over 10,000 clients across India. We manage a combined portfolio of over 500 crore rupees and have been in operation for over 8 years."
    },


    # ── SERVICES ─────────────────────────────────────────
    {
        "question": "What services does WealthWise offer?",
        "answer": "WealthWise offers six core services: financial planning, mutual fund advisory, tax planning, retirement planning, insurance advisory, and portfolio review. Each service is personalised based on your income, goals, and risk appetite."
    },
    {
        "question": "Do you offer mutual fund advisory?",
        "answer": "Yes, we offer comprehensive mutual fund advisory. Our advisors help you choose the right funds based on your goals, risk tolerance, and investment horizon. We cover equity funds, debt funds, hybrid funds, and ELSS for tax saving."
    },
    {
        "question": "Can you help with tax planning?",
        "answer": "Absolutely. Our tax planning service helps you legally minimise your tax liability using instruments like ELSS, PPF, NPS, HRA, and home loan deductions under sections 80C, 80D, and 24B. We work with both salaried and self-employed clients."
    },
    {
        "question": "Do you offer retirement planning?",
        "answer": "Yes, retirement planning is one of our most popular services. We help you calculate your retirement corpus, suggest the right mix of instruments, and create a step-by-step savings plan to meet your retirement goal."
    },
    {
        "question": "What is portfolio review service?",
        "answer": "In our portfolio review service, our advisor analyses your existing investments across mutual funds, stocks, fixed deposits, insurance, and real estate. We identify underperforming assets, suggest rebalancing, and ensure your portfolio is aligned with your current goals."
    },
    {
        "question": "Do you offer insurance advisory?",
        "answer": "Yes, we help you understand and choose the right term insurance, health insurance, and other insurance plans. We are not tied to any specific insurance company, so our advice is completely unbiased and based purely on your needs."
    },
    {
        "question": "Can you help with SIP investments?",
        "answer": "Yes, we help you start and manage SIPs in mutual funds. Our advisors discuss SIP amounts, frequency, and fund selection based on your monthly income and financial goals. We also review your SIPs periodically."
    },
    {
        "question": "Do you help with stock market investments?",
        "answer": "We provide guidance on equity investing and help you think about long-term wealth creation through fundamentally strong stocks and mutual funds. However, we do not provide short-term trading tips or intraday advice."
    },
    {
        "question": "Can you help NRIs with financial planning?",
        "answer": "Yes, we work with NRI clients extensively. We help NRIs with NRE and NRO account investments, repatriation of funds, DTAA benefits, and building an India-based investment portfolio aligned with their foreign income."
    },


    # ── FEES & PRICING ───────────────────────────────────
    {
        "question": "What are your fees?",
        "answer": "WealthWise charges a transparent flat fee. A one-time comprehensive financial plan costs rupees 5,000. Our annual advisory retainer is rupees 15,000 per year which includes unlimited consultations and quarterly portfolio reviews. We do not earn any commission from product sales."
    },
    {
        "question": "Do you charge commission on mutual funds?",
        "answer": "No, we do not charge any commission. WealthWise operates on a fee-only model, meaning we charge only our advisory fee. We recommend direct plans of mutual funds which have lower expense ratios and higher returns compared to regular plans."
    },
    {
        "question": "Is the first consultation free?",
        "answer": "Yes, the first 30-minute discovery call with our advisor is completely free of charge. This helps us understand your financial situation and goals, and helps you evaluate whether WealthWise is the right fit for you."
    },
    {
        "question": "Do you offer EMI for advisory fees?",
        "answer": "Yes, our annual retainer of rupees 15,000 can be paid in quarterly installments of rupees 4,000 each. We accept payments via UPI, net banking, credit card, and cheque."
    },
    {
        "question": "Are there any hidden charges?",
        "answer": "No, WealthWise follows complete fee transparency. All charges are discussed upfront before you sign any agreement. There are no hidden fees, no exit charges, and no commissions from any financial product."
    },


    # ── APPOINTMENT & BOOKING ────────────────────────────
    {
        "question": "How do I book an appointment?",
        "answer": "You can book an appointment right here through this voice assistant. Just tell me you want to book and I will collect your name, phone number, email address, and preferred time, and schedule an online session with our advisor."
    },
    {
        "question": "What details do you need to book a call?",
        "answer": "We need your name, phone number, email address, and your preferred date and time for the call. Your email is used to send the booking confirmation and the Google Meet link for the session."
    },
    {
        "question": "What happens after I book an appointment?",
        "answer": "After booking, you will receive a confirmation email along with a Google Meet link for the session. Our advisor will be on the call at the scheduled time. For the first call, you do not need to prepare anything — just join the meeting at the time you selected."
    },
    {
        "question": "How long does an advisory session last?",
        "answer": "The first free discovery call is 30 minutes. A comprehensive financial planning session is typically 60 to 90 minutes. Follow-up review sessions are 30 to 45 minutes."
    },
    {
        "question": "How soon can I get an appointment?",
        "answer": "We offer slots for today and tomorrow only. If you book today, you can get a slot as early as the same day depending on availability. The voice assistant will show you the available times and you can pick what suits you."
    },
    {
        "question": "Do you offer same-day appointments?",
        "answer": "Yes, same-day slots are available if the calendar has an opening. Our assistant will show you today's available times when you ask to book. If today is fully booked, we will offer you tomorrow's slots."
    },
    {
        "question": "Can I reschedule or cancel my appointment?",
        "answer": "Yes, you can reschedule or cancel at any time by calling 1800-XXX-XXXX or emailing support@wealthwise.in at least 4 hours before your scheduled time. There is no cancellation fee."
    },
    {
        "question": "What if I miss my appointment?",
        "answer": "No problem. If you miss your scheduled call, please contact us and we will reschedule at a time that works for you. We understand schedules can change and we are happy to accommodate."
    },
    {
        "question": "Can I choose a specific advisor?",
        "answer": "At this stage, we assign the most suitable available advisor based on your profile. If you have previously worked with a WealthWise advisor and wish to continue with the same person, please mention their name and we will do our best to accommodate that."
    },
    {
        "question": "Will the advisor call me or will I get a meeting link?",
        "answer": "You will receive a Google Meet link on your email at the time of booking. All first sessions are conducted online via Google Meet. In-person meetings at our offices are available only for follow-up sessions, by prior appointment."
    },
    {
        "question": "Is the advisory session online or in person?",
        "answer": "The first session is always conducted online via Google Meet. In-person meetings at our Mumbai, Pune, Bangalore, and Delhi offices are available only for follow-up sessions, by prior appointment."
    },
    {
        "question": "Can I book an appointment for my parents?",
        "answer": "Yes, you can book on behalf of your parents or any family member. Just provide their name and contact number, or yours if you prefer our advisor to call you first and then connect with them."
    },
    {
        "question": "I am not in India. Can I still book?",
        "answer": "Yes, we work with clients outside India as well, particularly NRIs. You can book a session and our advisor will connect with you via Google Meet at a mutually convenient time across time zones."
    },
    {
        "question": "What language do advisors speak?",
        "answer": "Our advisors primarily conduct sessions in English and Hindi. Several advisors also speak Marathi, Gujarati, Tamil, and Kannada. If you have a language preference, please mention it while booking and we will try to match you with a suitable advisor."
    },


    # ── FIRST CALL & SESSION ─────────────────────────────
    {
        "question": "What happens in the first call?",
        "answer": "The first call is a free 30-minute discovery session. Our advisor will ask about your current financial situation, your short and long-term goals, and any specific concerns you have. There is no commitment required and no products will be sold on this call."
    },
    {
        "question": "Is the first call free?",
        "answer": "Yes, the first 30-minute discovery call is completely free. No credit card is needed, no trial period, and no hidden charges. It is our way of letting you evaluate whether WealthWise is the right fit before you commit to anything."
    },
    {
        "question": "Is this a video call or a phone call?",
        "answer": "The first session is a video call via Google Meet. You will receive the meeting link on your email at the time of booking. You can join from your phone, tablet, or laptop. In-person meetings at our offices are only available for follow-up sessions by prior appointment."
    },
    {
        "question": "Do I need to prepare anything before the call?",
        "answer": "No preparation is needed for the first call. Just be ready to have a conversation about your financial goals. If you want to make the most of the session, you can optionally have a rough idea of your monthly income, existing investments, and key goals."
    },
    {
        "question": "Will I get a report after the session?",
        "answer": "For the free discovery call, you will receive a brief summary email with key discussion points and suggested next steps. Detailed written financial plans and portfolio reports are part of our paid advisory packages."
    },
    {
        "question": "Is this a sales call?",
        "answer": "No. The first call is a discovery session, not a sales call. Our advisor will listen to your goals and explain how WealthWise can help. There is no pressure to sign up and no products will be pitched during the call."
    },
    {
        "question": "What documents do I need for financial planning?",
        "answer": "For the first free call, no documents are needed. For a comprehensive financial planning session, it helps to have your recent salary slips, Form 16, bank statements, existing investment statements, insurance policy details, and a list of your liabilities. Our advisor will guide you on what to bring before any paid session."
    },
    {
        "question": "What happens after the first call?",
        "answer": "After the discovery call, our advisor will send you a brief summary email with key discussion points and suggested next steps. If you decide to proceed, the advisor will recommend the right paid package for your situation. There is no pressure — you can take your time to decide."
    },
    {
        "question": "What are the paid packages after the first call?",
        "answer": "We offer two paid options. A one-time comprehensive financial plan for rupees 5,000, which is a detailed written plan covering all your goals. Or an annual retainer for rupees 15,000 per year, which includes unlimited consultations, quarterly portfolio reviews, and annual plan updates. Fees can be paid via UPI, net banking, or credit card."
    },
    {
        "question": "How many sessions are included in the paid plan?",
        "answer": "The one-time plan includes one comprehensive planning session of 60 to 90 minutes plus a detailed written report. The annual retainer includes unlimited consultations throughout the year plus four quarterly portfolio review sessions of 30 to 45 minutes each."
    },
    {
        "question": "Are follow-up sessions also online?",
        "answer": "Follow-up sessions are primarily conducted online via Google Meet. In-person meetings at our Mumbai, Pune, Bangalore, and Delhi offices are available for annual retainer clients by prior appointment."
    },


    # ── TRUST & TRANSPARENCY ─────────────────────────────
    {
        "question": "Is this really free or is there a catch?",
        "answer": "The first 30-minute call is genuinely free with no conditions attached. We offer it so you can evaluate whether WealthWise is the right fit for you before committing to any paid plan. There is no obligation to sign up after the call."
    },
    {
        "question": "Will you try to sell me products?",
        "answer": "No. WealthWise is a fee-only advisor, which means we earn only from our advisory fees, not from selling financial products. We have no incentive to push any specific mutual fund, insurance, or investment product."
    },
    {
        "question": "Why should I trust WealthWise?",
        "answer": "WealthWise is a SEBI-registered Investment Advisor, which means we are regulated and accountable. We operate on a fee-only model with no commission conflicts. All our advisors are CFP certified with at least 5 years of experience. We have served over 10,000 clients across India over the past 8 years."
    },
    {
        "question": "How are you different from other advisors?",
        "answer": "Three things set us apart. First, we are fee-only — no commissions, no product bias. Second, all our advisors are CFP certified with a minimum of 5 years of experience. Third, we take a goals-based approach where every recommendation is tied to your specific life goals, not generic advice."
    },
    {
        "question": "Can I trust WealthWise with my investments?",
        "answer": "Yes. WealthWise does not hold or handle your money at any point. All investments are made directly in your name through SEBI-regulated AMCs and brokers. We are a fee-only SEBI-registered advisor, so we only provide advice. You always remain in full control of your funds."
    },
    {
        "question": "How is my data kept safe with WealthWise?",
        "answer": "WealthWise follows strict data privacy practices. Your personal and financial data is encrypted and stored securely. We do not share your information with any third party without your explicit consent. We are compliant with all SEBI data protection guidelines."
    },
    {
        "question": "Do you provide ongoing support after the plan is made?",
        "answer": "Yes, our annual retainer clients receive quarterly portfolio reviews, unlimited email and phone support, and annual financial plan updates. We aim to be your long-term financial partner, not just a one-time consultant."
    },

]