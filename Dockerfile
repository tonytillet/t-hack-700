##############
#    Base    #
##############

FROM python:3.11-slim AS base
WORKDIR /app

##############
#    Deps    #
##############

FROM base AS deps

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#####################
#    Development    #
#####################

FROM deps AS development

EXPOSE 8501

# python scripts/collect_ckan_real.py && \
CMD sh -c "\
    streamlit run main.py \
        --server.port=8501 \
        --server.headless=true \
"

#################
#    Builder    #
#################

FROM deps AS builder

# Copy application files
COPY . .
RUN python scripts/collect_ckan_real.py

################
#    Runner    #
################

FROM deps AS runner

# Copy built app
COPY --from=builder /app /app

EXPOSE 8501

CMD sh -c "\
    streamlit run main.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
"
