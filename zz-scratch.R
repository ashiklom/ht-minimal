fname <- "test-outputs/test-lrt.txt"
dat <- read.table(fname)
plot(V2 ~ V1, data = dat, type = "l")
