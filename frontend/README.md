# Big Data Optimizer Frontend

This is the **frontend** for the Big Data Optimizer project, built with [Next.js](https://nextjs.org).  
It provides a user interface for managing repositories, uploading large CSV files, monitoring processing jobs, and visualizing results.

---

## 🚀 Getting Started

### 1. **Install dependencies**

```bash
npm install
# or
yarn install
# or
pnpm install
# or
bun install
```

### 2. **Run the development server**

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the app.

---

## 🛠️ Project Structure

- `/src/app/` — Main Next.js app directory (pages, components, layouts)
- `/src/components/` — Reusable React components
- `public/` — Static assets

---

## ⚙️ Features

- **Repository Management:** Create, update, and view data repositories.
- **File Upload:** Upload large CSV files for processing.
- **Batch Processing:** Monitor the status of data processing jobs.
- **Results Visualization:** View and validate processing results and metrics.
- **Responsive UI:** Built with modern React and Next.js best practices.

---

## 📦 Environment Variables

If your frontend needs to connect to a backend API, create a `.env.local` file in this directory and set (check the `.env.local.example` file):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Adjust the URL as needed for your backend.

---

## 📝 Customization

- Edit `app/page.js` or other files in `app/` to customize pages.
- Add new components in `components/` as needed.
- Update styles in `styles/`.

---

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Big Data Optimizer Backend](../backend/README.md) (for API details)

---

## 🚀 Deployment

The recommended way to deploy this frontend is with [Vercel](https://vercel.com/) or any platform that supports Next.js.

See [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---

## 🤝 Contributing

Pull requests and feedback are welcome!  
Please open an issue or submit a PR if you have suggestions or improvements.

---

## License

This project is licensed under the MIT License.