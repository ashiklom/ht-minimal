fname <- "test-outputs/test-lrt.txt"
dat <- read.table(fname)
plot(V2 ~ V1, data = dat, type = "l")

##################################################
library(raster)

true_refl <- read.table("data/prosail-example.txt")
f <- "outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/output/simulated_toa_radiance"
f <- "outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/output/estimated_reflectance"
f <- "outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/output/estimated_state"
r <- brick(f)
x <- r[1,1][1,]
rx <- regexpr("[[:digit:]]{3,4}\\.[[:digit:]]+", names(x))
wl <- as.numeric(regmatches(names(x), rx))
plot(wl, x, type = 'l')

##################################################
library(tidyverse)

true_refl <- as_tibble(read.table("data/prosail-example.txt")) %>%
  select(wavelength = V1, value = V2) %>%
  mutate(kind = "true")

out_summer <- read.table("outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/output/estimated_reflectance.txt") %>%
  as_tibble() %>%
  select(wavelength = V1, value = V2) %>%
  mutate(kind = "summer")

out_winter <- read.table("outputs/atm_midlatitude_winter__2017-06-01__1900__vzen_0.00/output/estimated_reflectance.txt") %>%
  as_tibble() %>%
  select(wavelength = V1, value = V2) %>%
  mutate(kind = "winter")

dat <- bind_rows(true_refl, out_summer, out_winter)

ggplot(dat) +
  aes(x = wavelength, y = value, color = kind) +
  geom_line()

dat_wide <- dat %>%
  pivot_wider(names_from = "kind", values_from = "value")

ggplot(dat_wide) +
  aes(x = wavelength, y = summer - winter) +
  geom_line()

##################################################
d0 <- read.table("outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/lut/LUT_AOT550-0.0010_H2OSTR-2.2160_alb0.out")
d025 <- read.table("outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/lut/LUT_AOT550-0.0010_H2OSTR-2.2160_alb025.out")
d05 <- read.table("outputs/atm_midlatitude_summer__2017-06-01__1900__vzen_0.00/lut/LUT_AOT550-0.0010_H2OSTR-2.2160_alb05.out")

wl <- d0$V1
irr <- d0$V3
irr_zero <- irr == 0
rhoatm <- d0$V2 / 10 / irr * pi
rhoatm[irr_zero] <- 0
rho025 <- d025$V2 / 10 / irr * pi
rho025[irr_zero] <- 0
rho05 <- d05$V2 / 10 / irr * pi
rho05[irr_zero] <- 0

s <- 2.8 * (2 * rho025 - rhoatm - rho05) / (rho025 - rho05)
sum(rho025 == rho05)
sum(rhoatm == rho05)
sum(rhoatm == rho05)
rho025[rho025 == rho05]
rho025[rho025 == rho05]
sum(rho025 == rho05)
sum(rho025 == 0)
sum(!is.finite(s))
plot(wl, s, type = 'l')

plot(V2 ~ V1, data = d0, type = "l")
plot(V2 ~ V1, data = d025, type = "l")
plot(V2 ~ V1, data = d05, type = "l")

subset(d05, V2 == 0)

plot(d025$V1, d025$V2 - d05$V2, type = 'l')

##################################################
library(tidyverse)
radfiles <- list.files("outputs", "simulated_toa_radiance.txt",
                       recursive = TRUE, full.names = TRUE)
names(radfiles) <- basename(dirname(dirname(radfiles)))

rad_data <- map_dfr(radfiles, read_table,
                    col_names = c("wavelength", "radiance"),
                    .id = "file")

ggplot(rad_data) +
  aes(x = wavelength, y = radiance, color = file) +
  geom_line()

##################################################
library(R.matlab)
f1 <- "~/projects/sbg-uncertainty/hypertrace/hypertrace_rc1/hypertrace/data/basemap_surface_model.mat"
m1 <- readMat(f1)

plot(m1$wl, m1$means, type = 'l')
lines(m1$wl, m1$means + sqrt(diag(drop(m1$covs))), col = 2, lty = "dashed")
lines(m1$wl, m1$means - sqrt(diag(drop(m1$covs))), col = 2, lty = "dashed")

f2 <- "~/projects/sbg-uncertainty/hypertrace/hypertrace_rc1/hypertrace/data/simple_surface_model.mat"

m1

wl <- seq(380, 2500, 10)
writeMat(
  con = "data/uninformative-prior.mat",
  normalize = "Euclidean",
  wl = t(wl),
  means = t(rep(0.5, length(wl))),
  covs = array(diag(0.5, length(wl)), c(1, length(wl), length(wl))),
  refwl = t(wl[!(wl > 1290 & wl < 1450) & !(wl > 1690 & wl < 2100)])
)
