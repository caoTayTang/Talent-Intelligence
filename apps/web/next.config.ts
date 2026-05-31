import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  transpilePackages: ["@talent-intelligence/shared"]
};

export default nextConfig;
