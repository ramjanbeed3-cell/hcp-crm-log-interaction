import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchHCPs, fetchInteractions, createInteraction } from '../api/client';

export const loadHCPs = createAsyncThunk('interactions/loadHCPs', async () => {
  return await fetchHCPs();
});

export const loadInteractions = createAsyncThunk(
  'interactions/loadInteractions',
  async (hcpId) => {
    return await fetchInteractions(hcpId);
  }
);

export const submitInteraction = createAsyncThunk(
  'interactions/submitInteraction',
  async (payload) => {
    return await createInteraction(payload);
  }
);

const interactionsSlice = createSlice({
  name: 'interactions',
  initialState: {
    hcps: [],
    selectedHcpId: null,
    interactions: [],
    lastResult: null,
    status: 'idle',
    error: null,
  },
  reducers: {
    setSelectedHcp(state, action) {
      state.selectedHcpId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadHCPs.fulfilled, (state, action) => {
        state.hcps = action.payload;
      })
      .addCase(loadInteractions.fulfilled, (state, action) => {
        state.interactions = action.payload;
      })
      .addCase(submitInteraction.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(submitInteraction.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.lastResult = action.payload;
        state.interactions.unshift(action.payload);
      })
      .addCase(submitInteraction.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { setSelectedHcp } = interactionsSlice.actions;
export default interactionsSlice.reducer;
